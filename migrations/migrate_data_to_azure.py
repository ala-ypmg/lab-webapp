#!/usr/bin/env python3
"""
Data Migration Script: SQLite to Azure SQL
==========================================

This script migrates data from the local SQLite database (instance/lab_data.db)
to Azure SQL databases (users and ezeos).

Migration Order:
    1. users (users database)
    2. admin_users (users database)
    3. user_sessions (ezeos database)
    4. form_submissions (ezeos database)
    5. audit_log (ezeos database)

Features:
    - Preserves original IDs using SET IDENTITY_INSERT ON/OFF
    - Converts SQLite booleans to SQL Server BIT (0/1)
    - Batch inserts for performance
    - Progress indicators
    - Comprehensive error handling
    - Summary report

Usage:
    python migrations/migrate_data_to_azure.py

Prerequisites:
    - Azure SQL schema must be created first (run azure_sql_schema.sql)
    - Environment variables or manual configuration for Azure SQL credentials
    - pymssql installed (pip install pymssql)
"""

import os
import sys
import sqlite3
import pymssql
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# CONFIGURATION
# =============================================================================

# SQLite source database path
SQLITE_DB_PATH = "instance/lab_data.db"

# Azure SQL Server configuration
AZURE_SQL_SERVER = os.environ.get("AZURE_SQL_SERVER", "ezeos.database.windows.net")
AZURE_SQL_USERNAME = os.environ.get("AZURE_SQL_USERNAME", "ala")
AZURE_SQL_PASSWORD = os.environ.get("AZURE_SQL_PASSWORD", "")

# Database names
USERS_DATABASE = "users"
EZEOS_DATABASE = "ezeos"

# Batch size for inserts
BATCH_SIZE = 100

# =============================================================================
# TABLE DEFINITIONS
# =============================================================================

# Tables in 'users' database
USERS_DB_TABLES = {
    "users": {
        "columns": [
            "id", "user_id", "email", "passcode_hash", "created_at",
            "last_login", "is_active", "is_confirmed", "confirmed_at"
        ],
        "identity_column": "id",
        "boolean_columns": ["is_active", "is_confirmed"]
    },
    "admin_users": {
        "columns": ["id", "user_id", "admin_level", "created_at"],
        "identity_column": "id",
        "boolean_columns": []
    }
}

# Tables in 'ezeos' database
EZEOS_DB_TABLES = {
    "user_sessions": {
        "columns": [
            "id", "session_id", "user_id", "current_page", "max_page_reached",
            "started_at", "completed", "login_timestamp", "department", "remember_me",
            "ypb_daily_count_data", "final_block_time", "baked_ihcs_pt_link",
            "ihcs_in_pt_link", "non_baked_ihc", "ihcs_in_buffer_wash",
            "pathologist_requests_status", "request_source_email",
            "request_source_orchard", "request_source_send_out", "in_progress_her2",
            "upfront_special_stains", "peloris_maintenance", "notes"
        ],
        "identity_column": "id",
        "boolean_columns": [
            "completed", "remember_me", "baked_ihcs_pt_link", "ihcs_in_pt_link",
            "non_baked_ihc", "ihcs_in_buffer_wash", "request_source_email",
            "request_source_orchard", "request_source_send_out", "in_progress_her2"
        ]
    },
    "form_submissions": {
        "columns": [
            "id", "session_id", "user_id", "login_timestamp", "department",
            "remember_me", "ypb_daily_count_data", "final_block_time",
            "baked_ihcs_pt_link", "ihcs_in_pt_link", "non_baked_ihc",
            "ihcs_in_buffer_wash", "pathologist_requests_status",
            "request_source_email", "request_source_orchard",
            "request_source_send_out", "in_progress_her2",
            "upfront_special_stains", "peloris_maintenance", "notes", "submitted_at"
        ],
        "identity_column": "id",
        "boolean_columns": [
            "remember_me", "baked_ihcs_pt_link", "ihcs_in_pt_link",
            "non_baked_ihc", "ihcs_in_buffer_wash", "request_source_email",
            "request_source_orchard", "request_source_send_out", "in_progress_her2"
        ]
    },
    "audit_log": {
        "columns": [
            "id", "user_id", "action", "table_name", "record_id",
            "timestamp", "ip_address", "details"
        ],
        "identity_column": "id",
        "boolean_columns": []
    }
}


# =============================================================================
# UTILITY CLASSES
# =============================================================================

class MigrationStats:
    """Tracks migration statistics for reporting."""
    
    def __init__(self):
        self.tables: Dict[str, Dict[str, Any]] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.errors: List[str] = []
    
    def start(self):
        """Mark migration start time."""
        self.start_time = datetime.now()
    
    def end(self):
        """Mark migration end time."""
        self.end_time = datetime.now()
    
    def add_table(self, table_name: str, source_count: int, migrated_count: int, 
                  skipped_count: int = 0, error_count: int = 0):
        """Record statistics for a table migration."""
        self.tables[table_name] = {
            "source_count": source_count,
            "migrated_count": migrated_count,
            "skipped_count": skipped_count,
            "error_count": error_count
        }
    
    def add_error(self, error_msg: str):
        """Record an error message."""
        self.errors.append(error_msg)
    
    def print_report(self):
        """Print comprehensive migration report."""
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY REPORT")
        print("=" * 70)
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"\nMigration Duration: {duration:.2f} seconds")
            print(f"Started:  {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Finished: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "-" * 70)
        print(f"{'Table Name':<25} {'Source':>10} {'Migrated':>10} {'Skipped':>10} {'Errors':>10}")
        print("-" * 70)
        
        total_source = 0
        total_migrated = 0
        total_skipped = 0
        total_errors = 0
        
        for table, stats in self.tables.items():
            print(f"{table:<25} {stats['source_count']:>10} {stats['migrated_count']:>10} "
                  f"{stats['skipped_count']:>10} {stats['error_count']:>10}")
            total_source += stats['source_count']
            total_migrated += stats['migrated_count']
            total_skipped += stats['skipped_count']
            total_errors += stats['error_count']
        
        print("-" * 70)
        print(f"{'TOTAL':<25} {total_source:>10} {total_migrated:>10} "
              f"{total_skipped:>10} {total_errors:>10}")
        
        if self.errors:
            print("\n" + "-" * 70)
            print("ERRORS:")
            print("-" * 70)
            for error in self.errors:
                print(f"  • {error}")
        
        print("\n" + "=" * 70)
        
        # Overall status
        if total_errors == 0 and total_migrated == total_source:
            print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        elif total_errors > 0:
            print("⚠️  MIGRATION COMPLETED WITH ERRORS")
        else:
            print("⚠️  MIGRATION COMPLETED WITH WARNINGS")
        
        print("=" * 70 + "\n")


class ProgressIndicator:
    """Simple progress indicator for batch operations."""
    
    def __init__(self, total: int, table_name: str):
        self.total = total
        self.current = 0
        self.table_name = table_name
    
    def update(self, count: int = 1):
        """Update progress count."""
        self.current += count
        self._print()
    
    def _print(self):
        """Print progress bar."""
        if self.total == 0:
            return
        
        percent = (self.current / self.total) * 100
        bar_length = 40
        filled = int(bar_length * self.current / self.total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r  [{bar}] {percent:>5.1f}% ({self.current}/{self.total}) {self.table_name}", 
              end="", flush=True)
    
    def complete(self):
        """Mark progress as complete."""
        print()  # New line after progress bar


# =============================================================================
# DATABASE CONNECTION FUNCTIONS
# =============================================================================

def get_sqlite_connection() -> sqlite3.Connection:
    """Create connection to SQLite database."""
    if not os.path.exists(SQLITE_DB_PATH):
        raise FileNotFoundError(f"SQLite database not found: {SQLITE_DB_PATH}")
    
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_azure_connection(database: str, timeout: int = 60) -> pymssql.Connection:
    """
    Create connection to Azure SQL database.

    Args:
        database: Database name ('users' or 'ezeos')
        timeout: Connection timeout in seconds

    Returns:
        pymssql.Connection object
    """
    if not AZURE_SQL_PASSWORD:
        raise ValueError(
            "Azure SQL password not set. Set AZURE_SQL_PASSWORD environment variable "
            "or update AZURE_SQL_PASSWORD in this script."
        )

    print(f"  Connecting to Azure SQL ({database})...", end=" ", flush=True)
    conn = pymssql.connect(
        server=AZURE_SQL_SERVER,
        user=AZURE_SQL_USERNAME,
        password=AZURE_SQL_PASSWORD,
        database=database,
        tds_version='7.4',
        login_timeout=timeout,
    )
    print("Connected.")
    return conn


# =============================================================================
# DATA CONVERSION FUNCTIONS
# =============================================================================

def convert_boolean_to_bit(value: Any) -> Optional[int]:
    """
    Convert SQLite boolean to SQL Server BIT (0/1).
    
    SQLite stores booleans as 0/1 or True/False.
    SQL Server uses BIT which only accepts 0 or 1.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, int):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.lower() in ('true', '1', 'yes') else 0
    return int(bool(value))


def convert_row_for_azure(row: Dict[str, Any], boolean_columns: List[str]) -> Dict[str, Any]:
    """
    Convert a SQLite row dictionary for Azure SQL compatibility.
    
    Args:
        row: Dictionary of column names to values
        boolean_columns: List of column names that should be converted to BIT
    
    Returns:
        Converted row dictionary
    """
    converted = dict(row)
    
    for col in boolean_columns:
        if col in converted:
            converted[col] = convert_boolean_to_bit(converted[col])
    
    return converted


# =============================================================================
# MIGRATION FUNCTIONS
# =============================================================================

def get_table_columns_from_sqlite(sqlite_conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Get list of column names from SQLite table."""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns


def get_source_data(sqlite_conn: sqlite3.Connection, table_name: str, 
                    columns: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch all data from a SQLite table.
    
    Args:
        sqlite_conn: SQLite connection
        table_name: Name of table to read
        columns: List of columns to fetch
    
    Returns:
        List of row dictionaries
    """
    cursor = sqlite_conn.cursor()
    
    # Get actual columns that exist in SQLite table
    sqlite_columns = get_table_columns_from_sqlite(sqlite_conn, table_name)
    
    # Only select columns that exist in both SQLite and target schema
    common_columns = [col for col in columns if col in sqlite_columns]
    
    if not common_columns:
        print(f"  Warning: No common columns found for table {table_name}")
        return []
    
    columns_str = ", ".join(common_columns)
    query = f"SELECT {columns_str} FROM {table_name}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    return [dict(zip(common_columns, row)) for row in rows]


def check_table_exists(azure_conn: pymssql.Connection, table_name: str) -> bool:
    """Check if a table exists in Azure SQL database."""
    cursor = azure_conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s",
        (table_name,)
    )
    result = cursor.fetchone()
    return result[0] > 0 if result else False


def get_existing_ids(azure_conn: pymssql.Connection, table_name: str,
                     id_column: str) -> set:
    """Get set of existing IDs from Azure SQL table."""
    cursor = azure_conn.cursor()
    cursor.execute(f"SELECT {id_column} FROM {table_name}")
    return {row[0] for row in cursor.fetchall()}


def migrate_table(
    sqlite_conn: sqlite3.Connection,
    azure_conn: pymssql.Connection,
    table_name: str,
    table_config: Dict[str, Any],
    stats: MigrationStats
) -> Tuple[int, int, int]:
    """
    Migrate a single table from SQLite to Azure SQL.
    
    Args:
        sqlite_conn: SQLite connection
        azure_conn: Azure SQL connection
        table_name: Name of table to migrate
        table_config: Configuration dict with columns, identity_column, boolean_columns
        stats: MigrationStats object for recording results
    
    Returns:
        Tuple of (migrated_count, skipped_count, error_count)
    """
    print(f"\n  Migrating table: {table_name}")
    
    columns = table_config["columns"]
    identity_column = table_config["identity_column"]
    boolean_columns = table_config["boolean_columns"]
    
    # Check if table exists in Azure
    if not check_table_exists(azure_conn, table_name):
        error_msg = f"Table '{table_name}' does not exist in Azure SQL. Run schema migration first."
        stats.add_error(error_msg)
        print(f"    ERROR: {error_msg}")
        return 0, 0, 1
    
    # Get source data
    print(f"    Reading from SQLite...", end=" ", flush=True)
    source_data = get_source_data(sqlite_conn, table_name, columns)
    source_count = len(source_data)
    print(f"{source_count} records found.")
    
    if source_count == 0:
        print(f"    No data to migrate.")
        stats.add_table(table_name, 0, 0, 0, 0)
        return 0, 0, 0
    
    # Get existing IDs to avoid duplicates
    existing_ids = get_existing_ids(azure_conn, table_name, identity_column)
    
    # Filter out records that already exist
    new_records = [
        r for r in source_data 
        if r.get(identity_column) not in existing_ids
    ]
    skipped_count = source_count - len(new_records)
    
    if skipped_count > 0:
        print(f"    Skipping {skipped_count} existing records.")
    
    if not new_records:
        print(f"    All records already exist in Azure SQL.")
        stats.add_table(table_name, source_count, 0, skipped_count, 0)
        return 0, skipped_count, 0
    
    # Get actual columns that exist in source data
    available_columns = [col for col in columns if col in new_records[0]]
    
    # Build insert query
    columns_str = ", ".join(available_columns)
    placeholders = ", ".join(["%s" for _ in available_columns])
    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    cursor = azure_conn.cursor()
    migrated_count = 0
    error_count = 0
    
    # Enable IDENTITY_INSERT
    print(f"    Enabling IDENTITY_INSERT...")
    cursor.execute(f"SET IDENTITY_INSERT {table_name} ON")
    
    # Progress indicator
    progress = ProgressIndicator(len(new_records), table_name)
    
    # Insert in batches
    try:
        for i in range(0, len(new_records), BATCH_SIZE):
            batch = new_records[i:i + BATCH_SIZE]
            
            for record in batch:
                try:
                    # Convert booleans to BIT
                    converted = convert_row_for_azure(record, boolean_columns)
                    
                    # Extract values in column order
                    values = [converted.get(col) for col in available_columns]
                    
                    cursor.execute(insert_query, values)
                    migrated_count += 1
                    
                except pymssql.Error as e:
                    error_count += 1
                    error_msg = f"Error inserting record {record.get(identity_column)} in {table_name}: {str(e)}"
                    stats.add_error(error_msg)
            
            # Commit batch
            azure_conn.commit()
            progress.update(len(batch))
        
        progress.complete()
        print(f"    Successfully migrated {migrated_count} records.")
        
    except Exception as e:
        error_msg = f"Batch error in {table_name}: {str(e)}"
        stats.add_error(error_msg)
        print(f"    ERROR: {error_msg}")
        error_count += 1
        
    finally:
        # Disable IDENTITY_INSERT
        try:
            cursor.execute(f"SET IDENTITY_INSERT {table_name} OFF")
            azure_conn.commit()
        except pymssql.Error:
            pass  # May already be off
    
    stats.add_table(table_name, source_count, migrated_count, skipped_count, error_count)
    return migrated_count, skipped_count, error_count


def migrate_database_tables(
    sqlite_conn: sqlite3.Connection,
    azure_conn: pymssql.Connection,
    tables: Dict[str, Dict[str, Any]],
    database_name: str,
    stats: MigrationStats
):
    """
    Migrate all tables for a specific database.
    
    Args:
        sqlite_conn: SQLite connection
        azure_conn: Azure SQL connection
        tables: Dictionary of table configurations
        database_name: Name of database being migrated to
        stats: MigrationStats object
    """
    print(f"\n{'=' * 50}")
    print(f"Migrating to '{database_name}' database")
    print("=" * 50)
    
    for table_name, table_config in tables.items():
        migrate_table(sqlite_conn, azure_conn, table_name, table_config, stats)


# =============================================================================
# MAIN MIGRATION FUNCTION
# =============================================================================

def run_migration():
    """
    Execute the complete data migration from SQLite to Azure SQL.
    """
    print("\n" + "=" * 70)
    print("DATA MIGRATION: SQLite → Azure SQL")
    print("=" * 70)
    print(f"\nSource: {SQLITE_DB_PATH}")
    print(f"Target Server: {AZURE_SQL_SERVER}")
    print(f"Target Databases: {USERS_DATABASE}, {EZEOS_DATABASE}")
    print(f"Batch Size: {BATCH_SIZE}")
    
    stats = MigrationStats()
    stats.start()
    
    # Validate Azure SQL password is set
    if not AZURE_SQL_PASSWORD:
        print("\n❌ ERROR: Azure SQL password not configured.")
        print("   Set the AZURE_SQL_PASSWORD environment variable:")
        print("   export AZURE_SQL_PASSWORD='your-password-here'")
        print("   or update AZURE_SQL_PASSWORD in this script.")
        sys.exit(1)
    
    # Connect to SQLite
    print("\n" + "-" * 50)
    print("Step 1: Connect to source database (SQLite)")
    print("-" * 50)
    
    try:
        sqlite_conn = get_sqlite_connection()
        print(f"  ✓ Connected to SQLite: {SQLITE_DB_PATH}")
    except FileNotFoundError as e:
        print(f"  ❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ ERROR connecting to SQLite: {e}")
        sys.exit(1)
    
    # Migrate to 'users' database
    print("\n" + "-" * 50)
    print("Step 2: Migrate to 'users' database")
    print("-" * 50)
    
    try:
        users_conn = get_azure_connection(USERS_DATABASE)
        migrate_database_tables(sqlite_conn, users_conn, USERS_DB_TABLES, USERS_DATABASE, stats)
        users_conn.close()
        print(f"\n  ✓ Completed migration to '{USERS_DATABASE}' database")
    except pymssql.Error as e:
        error_msg = f"Failed to connect to '{USERS_DATABASE}' database: {e}"
        stats.add_error(error_msg)
        print(f"\n  ❌ ERROR: {error_msg}")
    
    # Migrate to 'ezeos' database
    print("\n" + "-" * 50)
    print("Step 3: Migrate to 'ezeos' database")
    print("-" * 50)
    
    try:
        ezeos_conn = get_azure_connection(EZEOS_DATABASE)
        migrate_database_tables(sqlite_conn, ezeos_conn, EZEOS_DB_TABLES, EZEOS_DATABASE, stats)
        ezeos_conn.close()
        print(f"\n  ✓ Completed migration to '{EZEOS_DATABASE}' database")
    except pymssql.Error as e:
        error_msg = f"Failed to connect to '{EZEOS_DATABASE}' database: {e}"
        stats.add_error(error_msg)
        print(f"\n  ❌ ERROR: {error_msg}")
    
    # Close SQLite connection
    sqlite_conn.close()
    
    # Complete migration
    stats.end()
    stats.print_report()
    
    # Return exit code based on results
    if stats.errors:
        sys.exit(1)
    sys.exit(0)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    run_migration()
