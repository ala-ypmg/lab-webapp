"""
Database connection utilities for Azure SQL and SQLite
Supports dual database architecture (users db and main db)
"""

import os
import time
import logging
from threading import Lock

logger = logging.getLogger(__name__)

# --- Connection health cache ---
# Tracks whether Azure SQL is reachable so we can fast-fail instead of
# blocking for login_timeout seconds on every request when the server is
# known-unreachable (e.g. firewall blocking the client IP, error 40615).
_connection_health: dict = {}   # {'users': (ok: bool, expires_at: float)}
_health_lock = Lock()

# How long (seconds) to cache a failure before retrying the real connection.
# During this window all requests fail immediately instead of hanging.
_FAILURE_CACHE_TTL = 30
# How long to cache a success (avoids re-probing healthy servers too often).
_SUCCESS_CACHE_TTL = 120

# Azure SQL error numbers that are permanent (firewall/auth); never retry these.
_PERMANENT_ERROR_CODES = {
    40615,  # IP not allowed by firewall
    18456,  # Login failed (bad credentials)
    40914,  # Cannot open server - tenant not found
    40532,  # Cannot open server requested by login (username missing @server suffix)
}

# Maximum retries for *transient* Azure SQL errors (e.g. 40613 – db not currently available).
_MAX_RETRIES = 2
_RETRY_BACKOFF_BASE = 1  # seconds

# Error 40613 = Serverless auto-pause wake-up in progress (can take 30-60s).
# Use a longer fixed delay instead of the standard backoff so the database
# has enough time to resume before we give up.
_AUTOPAUSE_ERROR_CODE = 40613
_AUTOPAUSE_RETRY_DELAY = 20  # seconds between retries while db is waking up
_AUTOPAUSE_MAX_RETRIES = 3   # up to ~60s total wait

# Database type detection
USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'

# Table to database mapping
# Tables in 'users' database: users, admin_users
# Tables in 'main' database: user_sessions, form_submissions, audit_log, accessioning_submissions, case_number_prefixes
TABLE_DATABASE_MAP = {
    'users': 'users',
    'admin_users': 'users',
    'user_sessions': 'main',
    'form_submissions': 'main',
    'audit_log': 'main',
    'accessioning_submissions': 'main',
    'case_number_prefixes': 'main',
}


def get_database_for_table(table_name):
    """
    Determine which database to use based on table name
    
    Args:
        table_name: Name of the table being accessed
        
    Returns:
        'users' or 'main' database name
    """
    return TABLE_DATABASE_MAP.get(table_name, 'main')


def get_azure_connection_params(database='users'):
    """
    Get Azure SQL connection parameters from environment variables
    
    Args:
        database: Which database to connect to ('users' or 'main')

    Returns:
        Dictionary of connection parameters for pymssql
    """
    server = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
    username = os.environ.get('AZURE_SQL_USERNAME', 'ala')
    password = os.environ.get('AZURE_SQL_PASSWORD', '')

    # Azure SQL requires SQL logins in `user@shortservername` form.
    # Always normalise: strip any existing @domain suffix (e.g. @ypmg.com set in
    # the env var) and re-append the correct short server name to avoid error 40532
    # where pymssql misreads the domain part as the target server.
    server_short = server.split('.', 1)[0]
    base_username = username.split('@')[0]
    username = f'{base_username}@{server_short}'

    # Select database based on parameter
    if database == 'users':
        db_name = os.environ.get('AZURE_SQL_DATABASE_USERS', 'users')
    else:
        db_name = os.environ.get('AZURE_SQL_DATABASE_MAIN', 'main')
    
    return {
        'server': server,
        'user': username,
        'password': password,
        'database': db_name,
        'tds_version': '7.4',  # Required for Azure SQL
        'login_timeout': 10,   # Reduced from 30s — fail fast when server is unreachable
    }


def _get_cached_health(database):
    """Return (is_healthy, is_cached) for the given database key."""
    with _health_lock:
        entry = _connection_health.get(database)
        if entry is None:
            return None, False
        ok, expires_at = entry
        if time.monotonic() < expires_at:
            return ok, True
        # Cache expired — remove stale entry
        del _connection_health[database]
        return None, False


def _set_cached_health(database, ok):
    ttl = _SUCCESS_CACHE_TTL if ok else _FAILURE_CACHE_TTL
    with _health_lock:
        _connection_health[database] = (ok, time.monotonic() + ttl)


def _extract_error_code(exc):
    """Extract the integer error code from a pymssql.Error if possible."""
    try:
        # pymssql.Error args: (code, message_bytes) or just (message,)
        if exc.args and isinstance(exc.args[0], int):
            return exc.args[0]
    except Exception:
        pass
    return None


def get_connection(database='users', for_table=None):
    """
    Get a database connection for Azure SQL or SQLite.

    For Azure SQL:
    - Fast-fails (within _FAILURE_CACHE_TTL seconds) when the server was
      recently found unreachable (e.g. firewall blocking client IP, error 40615).
    - Retries up to _MAX_RETRIES times for transient errors.
    - Permanent errors (firewall, bad credentials) are never retried.

    Args:
        database: Which database to connect to ('users' or 'main')
        for_table: Optional table name to auto-detect database

    Returns:
        Database connection object (pymssql.Connection or sqlite3.Connection)
    """
    # Auto-detect database from table name if provided
    if for_table:
        database = get_database_for_table(for_table)

    if USE_AZURE_SQL:
        import pymssql

        # Fast-fail if we already know this database is unreachable
        cached_ok, is_cached = _get_cached_health(database)
        if is_cached and not cached_ok:
            raise pymssql.OperationalError(
                f"Azure SQL '{database}' is currently unreachable (cached failure). "
                "Check firewall rules or server availability."
            )

        params = get_azure_connection_params(database)
        logger.info(
            f"Azure SQL connecting: server={params['server']} "
            f"database={params['database']} user={params['user']}"
        )
        last_exc = None

        # 40613 (Serverless auto-pause) needs its own retry loop with a longer
        # delay — the standard backoff loop is too fast for a cold-start wake-up.
        autopause_attempts = 0

        for attempt in range(_MAX_RETRIES + 1):
            try:
                conn = pymssql.connect(**params)
                logger.debug(f"Connected to Azure SQL database: {database}")
                _set_cached_health(database, True)
                return conn
            except pymssql.Error as e:
                last_exc = e
                error_code = _extract_error_code(e)

                if error_code == 40615:
                    logger.error(
                        f"Azure SQL connection blocked by firewall ({database}, error 40615). "
                        "The client IP is not whitelisted. "
                        "Fix: Azure Portal → SQL servers → ezeos → Security → Networking → "
                        "add a firewall rule for this server's outbound IP."
                    )
                    _set_cached_health(database, False)
                    raise

                if error_code in _PERMANENT_ERROR_CODES:
                    logger.error(f"Azure SQL permanent error ({database}, code {error_code}): {e}")
                    _set_cached_health(database, False)
                    raise

                if error_code == _AUTOPAUSE_ERROR_CODE:
                    autopause_attempts += 1
                    if autopause_attempts <= _AUTOPAUSE_MAX_RETRIES:
                        logger.warning(
                            f"Azure SQL Serverless database is waking from auto-pause "
                            f"({database}, attempt {autopause_attempts}/{_AUTOPAUSE_MAX_RETRIES}). "
                            f"Retrying in {_AUTOPAUSE_RETRY_DELAY}s. "
                            "To prevent this delay, disable auto-pause: "
                            "Azure Portal → SQL databases → Compute + storage → Auto-pause delay → No pause."
                        )
                        time.sleep(_AUTOPAUSE_RETRY_DELAY)
                        continue
                    else:
                        logger.error(
                            f"Azure SQL database did not finish waking from auto-pause after "
                            f"{_AUTOPAUSE_MAX_RETRIES} retries ({database}). "
                            "Disable auto-pause to prevent this: "
                            "Azure Portal → SQL databases → Compute + storage → Auto-pause delay → No pause."
                        )
                        _set_cached_health(database, False)
                        raise

                # Other transient error — retry with backoff
                if attempt < _MAX_RETRIES:
                    wait = _RETRY_BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        f"Azure SQL transient error ({database}, attempt {attempt + 1}/"
                        f"{_MAX_RETRIES + 1}, retrying in {wait}s): {e}"
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"Azure SQL connection error ({database}): {e}")
                    _set_cached_health(database, False)

        raise last_exc
    else:
        import sqlite3
        from flask import current_app
        db_path = current_app.config.get('DATABASE_URI')
        conn = sqlite3.connect(db_path)
        return conn


def get_users_connection():
    """Get connection to users database"""
    return get_connection(database='users')


def get_main_connection():
    """Get connection to main database"""
    return get_connection(database='main')


def execute_with_connection(database='users', for_table=None):
    """
    Context manager for database connections
    
    Usage:
        with execute_with_connection(for_table='users') as conn:
            cursor = conn.cursor()
            cursor.execute(...)
            conn.commit()
    """
    from contextlib import contextmanager
    
    @contextmanager
    def connection_context():
        conn = get_connection(database=database, for_table=for_table)
        try:
            yield conn
        finally:
            conn.close()
    
    return connection_context()


def get_lastrowid(cursor, use_azure=None):
    """
    Get the last inserted row ID (handles Azure SQL vs SQLite difference)
    
    Args:
        cursor: Database cursor after INSERT statement
        use_azure: Override for USE_AZURE_SQL (optional)
        
    Returns:
        The last inserted row ID
    """
    if use_azure is None:
        use_azure = USE_AZURE_SQL
        
    if use_azure:
        # Azure SQL uses SCOPE_IDENTITY()
        cursor.execute("SELECT SCOPE_IDENTITY()")
        result = cursor.fetchone()
        return int(result[0]) if result and result[0] else None
    else:
        # SQLite uses lastrowid
        return cursor.lastrowid


def row_to_dict(cursor, row):
    """
    Convert a row tuple to a dictionary using cursor description
    
    Args:
        cursor: Database cursor with column descriptions
        row: Row tuple from fetchone() or fetchall()
        
    Returns:
        Dictionary with column names as keys
    """
    if row is None:
        return None
    columns = [column[0] for column in cursor.description]
    return dict(zip(columns, row))


def verify_connection(database='users'):
    """
    Verify database connection is working

    Args:
        database: Which database to verify ('users' or 'main')
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        # Resolve the actual database name from env vars so the log reflects
        # what we're really connecting to (catches AZURE_SQL_DATABASE_MAIN
        # misconfiguration where the logical key says 'ezeos' but the real DB
        # is something else, e.g. 'main').
        if USE_AZURE_SQL:
            params = get_azure_connection_params(database)
            actual_db = params['database']
        else:
            actual_db = database
        conn = get_connection(database=database)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == 1:
            if actual_db != database:
                logger.warning(
                    f"Database connection verified for logical key '{database}' "
                    f"but actual database name is '{actual_db}'. "
                    f"Check AZURE_SQL_DATABASE_{database.upper()} env var."
                )
            else:
                logger.info(f"Database connection verified: {database}")
            return True
        return False
    except Exception as e:
        logger.error(f"Database connection verification failed ({database}): {e}")
        return False


def verify_all_connections():
    """
    Verify connections to all databases
    
    Returns:
        Dictionary with database names and their connection status
    """
    results = {}
    
    if USE_AZURE_SQL:
        results['users'] = verify_connection('users')
        results['main'] = verify_connection('main')
    else:
        # For SQLite, we only need to verify once
        results['sqlite'] = verify_connection()
        
    return results


def format_datetime_for_db(dt):
    """
    Format datetime for database storage (handles Azure SQL vs SQLite)
    
    Args:
        dt: datetime object
        
    Returns:
        Formatted datetime string or original datetime
    """
    if dt is None:
        return None
        
    if USE_AZURE_SQL:
        # Azure SQL prefers ISO format
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    else:
        # SQLite handles datetime objects directly
        return dt


def bool_to_db(value):
    """
    Convert Python boolean to database-appropriate value
    Azure SQL BIT columns expect 1/0, SQLite also works with 1/0
    
    Args:
        value: Boolean value
        
    Returns:
        1 for True, 0 for False, None for None
    """
    if value is None:
        return None
    return 1 if value else 0


def db_to_bool(value):
    """
    Convert database value to Python boolean
    
    Args:
        value: Database value (1/0, True/False, or None)
        
    Returns:
        Boolean value
    """
    if value is None:
        return None
    return bool(value)


class DatabaseConfig:
    """Configuration holder for database settings"""
    
    def __init__(self):
        self.use_azure_sql = USE_AZURE_SQL
        self.azure_server = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
        self.azure_username = os.environ.get('AZURE_SQL_USERNAME', 'ala')
        self.users_database = os.environ.get('AZURE_SQL_DATABASE_USERS', 'users')
        self.main_database = os.environ.get('AZURE_SQL_DATABASE_MAIN', 'main')

    def to_dict(self):
        """Return configuration as dictionary (excluding password)"""
        return {
            'use_azure_sql': self.use_azure_sql,
            'azure_server': self.azure_server,
            'azure_username': self.azure_username,
            'users_database': self.users_database,
            'main_database': self.main_database,
        }


# Global configuration instance
db_config = DatabaseConfig()
