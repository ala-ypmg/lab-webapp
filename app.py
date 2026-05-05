from flask import Flask, session as flask_session
from flask_login import LoginManager
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import config
import os
import sqlite3
from datetime import datetime
import bcrypt
import logging

# Initialize Flask app
app = Flask(__name__)

# Load configuration - detect Vercel or use FLASK_ENV
if os.environ.get('VERCEL'):
    env = 'vercel'
else:
    env = os.environ.get('FLASK_ENV', 'production')
app.config.from_object(config[env])

# Setup logging (before any logging calls)
from utils.logging_config import setup_logging
setup_logging(app)

logger = logging.getLogger(__name__)
logger.info(f"Application starting in {env.upper()} mode")

# Database configuration
USE_AZURE_SQL = app.config.get('USE_AZURE_SQL', False)
logger.info(f"Database mode: {'Azure SQL' if USE_AZURE_SQL else 'SQLite'}")

# Auto-initialization for Vercel (handles ephemeral /tmp storage) - SQLite only
def init_vercel_database(db_path):
    """Initialize database tables for Vercel deployment (SQLite)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON;')
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            passcode_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            is_confirmed BOOLEAN DEFAULT 0,
            confirmed_at TIMESTAMP
        )
    ''')
    
    # Create User Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(255) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            current_page INTEGER DEFAULT 1,
            max_page_reached INTEGER DEFAULT 1,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed BOOLEAN DEFAULT 0,
            login_timestamp TIMESTAMP,
            department VARCHAR(50),
            remember_me BOOLEAN DEFAULT 0,
            ypb_daily_count_data TEXT,
            final_block_time TIME,
            baked_ihcs_pt_link BOOLEAN,
            ihcs_in_pt_link BOOLEAN,
            non_baked_ihc BOOLEAN,
            ihcs_in_buffer_wash BOOLEAN,
            pathologist_requests_status VARCHAR(20),
            request_source_email BOOLEAN,
            request_source_orchard BOOLEAN,
            request_source_send_out BOOLEAN,
            in_progress_her2 BOOLEAN,
            upfront_special_stains VARCHAR(20),
            peloris_maintenance VARCHAR(20),
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create Form Submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            login_timestamp TIMESTAMP NOT NULL,
            department VARCHAR(50) NOT NULL,
            remember_me BOOLEAN DEFAULT 0,
            ypb_daily_count_data TEXT,
            final_block_time TIME,
            baked_ihcs_pt_link BOOLEAN,
            ihcs_in_pt_link BOOLEAN,
            non_baked_ihc BOOLEAN,
            ihcs_in_buffer_wash BOOLEAN,
            pathologist_requests_status VARCHAR(20),
            request_source_email BOOLEAN,
            request_source_orchard BOOLEAN,
            request_source_send_out BOOLEAN,
            in_progress_her2 BOOLEAN,
            upfront_special_stains VARCHAR(20),
            peloris_maintenance VARCHAR(20),
            notes TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES user_sessions(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create Admin Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            admin_level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create Audit Log table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action VARCHAR(100) NOT NULL,
            table_name VARCHAR(50),
            record_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create Accessioning Submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accessioning_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submission_data TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON user_sessions(session_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_submissions_user_id ON form_submissions(user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_submissions_department ON form_submissions(department);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_submissions_timestamp ON form_submissions(submitted_at);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user_id ON audit_log(user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_accessioning_user_id ON accessioning_submissions(user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_accessioning_submitted_at ON accessioning_submissions(submitted_at);')

    conn.commit()
    conn.close()
    logger.info(f"Vercel database initialized at: {db_path}")

def seed_vercel_users(db_path):
    """Seed initial users for Vercel deployment (SQLite)"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users already exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] > 0:
        conn.close()
        logger.info("Vercel users already seeded, skipping")
        return
    
    # Define initial users (user_id, email, passcode)
    initial_users = [
        ('ala', 'ala@ypmg.com', '6925'),
        ('user1', 'user1@ypmg.com', '1111'),
        ('user2', 'user2@ypmg.com', '2222'),
        ('histology_tech', 'histology_tech@ypmg.com', '3333'),
        ('cytotech', 'cytotech@ypmg.com', '4444'),
        ('labmanager', 'labmanager@ypmg.com', '5555'),
    ]
    
    # Create users (auto-confirmed to bypass email verification)
    created_users = {}
    for user_id, email, passcode in initial_users:
        passcode_hash = bcrypt.hashpw(passcode.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            cursor.execute('''
                INSERT INTO users (user_id, email, passcode_hash, created_at, is_confirmed, confirmed_at)
                VALUES (?, ?, ?, ?, 1, ?)
            ''', (user_id, email.lower(), passcode_hash, datetime.now(), datetime.now()))
            created_users[user_id] = cursor.lastrowid
            logger.info(f"Created user: {user_id} [AUTO-CONFIRMED]")
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    # Create admin users
    admin_assignments = [
        ('ala', 3),        # Full admin access
        ('labmanager', 2), # Export and submissions access
    ]
    
    for user_id, admin_level in admin_assignments:
        if user_id in created_users:
            db_user_id = created_users[user_id]
            cursor.execute('''
                INSERT INTO admin_users (user_id, admin_level)
                VALUES (?, ?)
            ''', (db_user_id, admin_level))
            logger.info(f"Created admin user: {user_id} (Level {admin_level})")
    
    conn.commit()
    conn.close()
    logger.info("User seeding complete")


def verify_azure_sql_connection():
    """Verify Azure SQL connection on startup"""
    try:
        from utils.db_connection import verify_all_connections
        results = verify_all_connections()

        all_ok = all(results.values())
        if all_ok:
            logger.info("All Azure SQL database connections verified successfully")
            for db_name, status in results.items():
                logger.info(f"  - {db_name}: {'OK' if status else 'FAILED'}")
        else:
            failed_dbs = [db for db, status in results.items() if not status]
            logger.error(f"Azure SQL connection verification failed for: {', '.join(failed_dbs)}")
            raise RuntimeError(f"Database connection failed for: {', '.join(failed_dbs)}")

        return all_ok
    except ImportError as e:
        logger.error(f"Failed to import database connection utilities: {e}")
        raise
    except Exception as e:
        logger.error(f"Azure SQL connection verification error: {e}")
        raise


def init_azure_sql_schema():
    """
    Idempotently create all Azure SQL tables on startup.

    The connection-verification step only confirms the server is reachable
    (SELECT 1); it does NOT verify that the application tables exist.  Running
    CREATE TABLE with an IF NOT EXISTS guard on every boot is safe and ensures
    the schema is always present — matching what init_vercel_database() does for
    the SQLite/Vercel path.
    """
    from utils.db_connection import get_users_connection, get_main_connection

    # ------------------------------------------------------------------ users db
    users_ddl = [
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
        CREATE TABLE users (
            id            INT PRIMARY KEY IDENTITY(1,1),
            user_id       NVARCHAR(50)  NOT NULL,
            email         NVARCHAR(255) NOT NULL,
            passcode_hash NVARCHAR(255) NOT NULL,
            created_at    DATETIME2     DEFAULT GETDATE(),
            last_login    DATETIME2     NULL,
            is_active     BIT           DEFAULT 1,
            is_confirmed  BIT           DEFAULT 0,
            confirmed_at  DATETIME2     NULL,
            CONSTRAINT UQ_users_user_id UNIQUE (user_id),
            CONSTRAINT UQ_users_email   UNIQUE (email)
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_user_id' AND object_id = OBJECT_ID('users')) CREATE INDEX idx_users_user_id ON users(user_id)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email'   AND object_id = OBJECT_ID('users')) CREATE INDEX idx_users_email   ON users(email)",
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_users')
        CREATE TABLE admin_users (
            id          INT PRIMARY KEY IDENTITY(1,1),
            user_id     INT           NOT NULL,
            admin_level INT           DEFAULT 1,
            created_at  DATETIME2     DEFAULT GETDATE(),
            CONSTRAINT FK_admin_users_user FOREIGN KEY (user_id)
                REFERENCES users(id) ON DELETE CASCADE
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_admin_users_user_id' AND object_id = OBJECT_ID('admin_users')) CREATE INDEX idx_admin_users_user_id ON admin_users(user_id)",
    ]

    conn = get_users_connection()
    try:
        cur = conn.cursor()
        for stmt in users_ddl:
            cur.execute(stmt)
            conn.commit()
        logger.info("Azure SQL 'users' database schema verified/created")
    finally:
        conn.close()

    # ------------------------------------------------------------------ main db
    main_ddl = [
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_sessions')
        CREATE TABLE user_sessions (
            id                          INT PRIMARY KEY IDENTITY(1,1),
            session_id                  NVARCHAR(255) NOT NULL,
            user_id                     INT           NOT NULL,
            current_page                INT           DEFAULT 1,
            max_page_reached            INT           DEFAULT 1,
            started_at                  DATETIME2     DEFAULT GETDATE(),
            completed                   BIT           DEFAULT 0,
            login_timestamp             DATETIME2     NULL,
            department                  NVARCHAR(50)  NULL,
            remember_me                 BIT           DEFAULT 0,
            ypb_daily_count_data        NVARCHAR(MAX) NULL,
            final_block_time            TIME          NULL,
            baked_ihcs_pt_link          NVARCHAR(10)  NULL,
            ihcs_in_pt_link             NVARCHAR(10)  NULL,
            non_baked_ihc               NVARCHAR(10)  NULL,
            ihcs_in_buffer_wash         NVARCHAR(10)  NULL,
            pathologist_requests_status NVARCHAR(20)  NULL,
            request_source_email        BIT           NULL,
            request_source_orchard      BIT           NULL,
            request_source_send_out     BIT           NULL,
            in_progress_her2            NVARCHAR(10)  NULL,
            upfront_special_stains      NVARCHAR(20)  NULL,
            peloris_maintenance         NVARCHAR(20)  NULL,
            notes                       NVARCHAR(MAX) NULL,
            CONSTRAINT UQ_user_sessions_session_id UNIQUE (session_id)
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sessions_user_id'   AND object_id = OBJECT_ID('user_sessions')) CREATE INDEX idx_sessions_user_id   ON user_sessions(user_id)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sessions_session_id' AND object_id = OBJECT_ID('user_sessions')) CREATE INDEX idx_sessions_session_id ON user_sessions(session_id)",
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'form_submissions')
        CREATE TABLE form_submissions (
            id                          INT PRIMARY KEY IDENTITY(1,1),
            session_id                  INT           NOT NULL,
            user_id                     INT           NOT NULL,
            login_timestamp             DATETIME2     NOT NULL,
            department                  NVARCHAR(50)  NOT NULL,
            remember_me                 BIT           DEFAULT 0,
            ypb_daily_count_data        NVARCHAR(MAX) NULL,
            final_block_time            TIME          NULL,
            baked_ihcs_pt_link          NVARCHAR(10)  NULL,
            ihcs_in_pt_link             NVARCHAR(10)  NULL,
            non_baked_ihc               NVARCHAR(10)  NULL,
            ihcs_in_buffer_wash         NVARCHAR(10)  NULL,
            pathologist_requests_status NVARCHAR(20)  NULL,
            request_source_email        BIT           NULL,
            request_source_orchard      BIT           NULL,
            request_source_send_out     BIT           NULL,
            in_progress_her2            NVARCHAR(10)  NULL,
            upfront_special_stains      NVARCHAR(20)  NULL,
            peloris_maintenance         NVARCHAR(20)  NULL,
            notes                       NVARCHAR(MAX) NULL,
            submitted_at                DATETIME2     DEFAULT GETDATE(),
            CONSTRAINT FK_form_submissions_session FOREIGN KEY (session_id)
                REFERENCES user_sessions(id) ON DELETE CASCADE
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_user_id'   AND object_id = OBJECT_ID('form_submissions')) CREATE INDEX idx_submissions_user_id   ON form_submissions(user_id)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_department' AND object_id = OBJECT_ID('form_submissions')) CREATE INDEX idx_submissions_department ON form_submissions(department)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_timestamp'  AND object_id = OBJECT_ID('form_submissions')) CREATE INDEX idx_submissions_timestamp  ON form_submissions(submitted_at)",
        # Migrate workflow status columns BIT → NVARCHAR(10) — unconditional, idempotent on SQL Server
        "ALTER TABLE user_sessions ALTER COLUMN baked_ihcs_pt_link NVARCHAR(10) NULL",
        "ALTER TABLE user_sessions ALTER COLUMN ihcs_in_pt_link NVARCHAR(10) NULL",
        "ALTER TABLE user_sessions ALTER COLUMN non_baked_ihc NVARCHAR(10) NULL",
        "ALTER TABLE user_sessions ALTER COLUMN ihcs_in_buffer_wash NVARCHAR(10) NULL",
        "ALTER TABLE user_sessions ALTER COLUMN in_progress_her2 NVARCHAR(10) NULL",
        "ALTER TABLE form_submissions ALTER COLUMN baked_ihcs_pt_link NVARCHAR(10) NULL",
        "ALTER TABLE form_submissions ALTER COLUMN ihcs_in_pt_link NVARCHAR(10) NULL",
        "ALTER TABLE form_submissions ALTER COLUMN non_baked_ihc NVARCHAR(10) NULL",
        "ALTER TABLE form_submissions ALTER COLUMN ihcs_in_buffer_wash NVARCHAR(10) NULL",
        "ALTER TABLE form_submissions ALTER COLUMN in_progress_her2 NVARCHAR(10) NULL",
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'audit_log')
        CREATE TABLE audit_log (
            id         INT PRIMARY KEY IDENTITY(1,1),
            user_id    INT           NOT NULL,
            action     NVARCHAR(100) NOT NULL,
            table_name NVARCHAR(50)  NULL,
            record_id  INT           NULL,
            timestamp  DATETIME2     DEFAULT GETDATE(),
            ip_address NVARCHAR(45)  NULL,
            details    NVARCHAR(MAX) NULL
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_audit_user_id'  AND object_id = OBJECT_ID('audit_log')) CREATE INDEX idx_audit_user_id  ON audit_log(user_id)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_audit_timestamp' AND object_id = OBJECT_ID('audit_log')) CREATE INDEX idx_audit_timestamp ON audit_log(timestamp)",
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'accessioning_submissions')
        CREATE TABLE accessioning_submissions (
            id              INT PRIMARY KEY IDENTITY(1,1),
            user_id         INT           NOT NULL,
            submitted_at    DATETIME2     DEFAULT GETDATE(),
            submission_data NVARCHAR(MAX) NOT NULL
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_accessioning_user_id'     AND object_id = OBJECT_ID('accessioning_submissions')) CREATE INDEX idx_accessioning_user_id     ON accessioning_submissions(user_id)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_accessioning_submitted_at' AND object_id = OBJECT_ID('accessioning_submissions')) CREATE INDEX idx_accessioning_submitted_at ON accessioning_submissions(submitted_at)",
        """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'case_number_prefixes')
        CREATE TABLE case_number_prefixes (
            id         INT PRIMARY KEY IDENTITY(1,1),
            prefix     NVARCHAR(20)  NOT NULL,
            facility   NVARCHAR(100) NOT NULL,
            is_active  BIT           DEFAULT 1,
            created_at DATETIME2     DEFAULT GETDATE(),
            CONSTRAINT UQ_case_number_prefixes_prefix UNIQUE (prefix)
        )
        """,
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_prefixes_facility'  AND object_id = OBJECT_ID('case_number_prefixes')) CREATE INDEX idx_prefixes_facility  ON case_number_prefixes(facility)",
        "IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_prefixes_is_active' AND object_id = OBJECT_ID('case_number_prefixes')) CREATE INDEX idx_prefixes_is_active ON case_number_prefixes(is_active)",
        """
        IF NOT EXISTS (SELECT 1 FROM case_number_prefixes)
        INSERT INTO case_number_prefixes (prefix, facility) VALUES
            ('KAS',   'AH Bakersfield'),
            ('KAB',   'AH Bakersfield'),
            ('KAN',   'AH Bakersfield'),
            ('KAF',   'AH Bakersfield'),
            ('KDS',   'AH Delano'),
            ('KDB',   'AH Delano'),
            ('KDN',   'AH Delano'),
            ('KDF',   'AH Delano'),
            ('KHS',   'AH Specialty Bakersfield'),
            ('KHB',   'AH Specialty Bakersfield'),
            ('KHN',   'AH Specialty Bakersfield'),
            ('KHF',   'AH Specialty Bakersfield'),
            ('KTS',   'AH Tehachapi'),
            ('KTB',   'AH Tehachapi'),
            ('KTN',   'AH Tehachapi'),
            ('KTF',   'AH Tehachapi'),
            ('KS',    'Bakersfield OP'),
            ('KB',    'Bakersfield OP'),
            ('KN',    'Bakersfield OP'),
            ('KF',    'Bakersfield OP'),
            ('TC-KPO','Bakersfield TC'),
            ('VKS',   'Kaweah Health Medical Center'),
            ('VKB',   'Kaweah Health Medical Center'),
            ('VKN',   'Kaweah Health Medical Center'),
            ('VKF',   'Kaweah Health Medical Center'),
            ('VVS',   'Visalia'),
            ('VVB',   'Visalia'),
            ('VVN',   'Visalia'),
            ('VVF',   'Visalia'),
            ('SVS',   'Visalia')
        """,
    ]

    conn = get_main_connection()
    try:
        cur = conn.cursor()
        for stmt in main_ddl:
            cur.execute(stmt)
            conn.commit()
        logger.info("Azure SQL 'main' database schema verified/created")
    finally:
        conn.close()


# Initialize database based on configuration
if USE_AZURE_SQL:
    # Azure SQL mode - verify connection then ensure schema exists
    logger.info("Initializing Azure SQL connections...")
    try:
        verify_azure_sql_connection()
        init_azure_sql_schema()
    except Exception as e:
        logger.critical(f"Azure SQL initialization failed: {e}")
        # Don't raise here - let the app start but log critical error
        # Individual requests will fail with appropriate error messages
elif env == 'vercel':
    # Vercel with SQLite - initialize database if it doesn't exist
    db_path = app.config['DATABASE_URI']
    if not os.path.exists(db_path):
        logger.info(f"Database not found at {db_path}, initializing...")
        init_vercel_database(db_path)
        seed_vercel_users(db_path)
    else:
        # Check if tables exist (in case /tmp persisted but is corrupted)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.warning("Database exists but tables missing, reinitializing...")
            conn.close()
            init_vercel_database(db_path)
            seed_vercel_users(db_path)
        else:
            conn.close()
            logger.info(f"Database verified at {db_path}")

# Run lightweight schema migrations for SQLite development environments.
# CREATE TABLE IF NOT EXISTS is idempotent — safe to run on every startup.
if not USE_AZURE_SQL and env != 'vercel':
    try:
        _db_path = app.config.get('DATABASE_URI')
        if _db_path and os.path.exists(_db_path):
            _conn = sqlite3.connect(_db_path)
            _cur = _conn.cursor()
            _cur.execute('''
                CREATE TABLE IF NOT EXISTS accessioning_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    submission_data TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            _cur.execute('CREATE INDEX IF NOT EXISTS idx_accessioning_user_id ON accessioning_submissions(user_id);')
            _cur.execute('CREATE INDEX IF NOT EXISTS idx_accessioning_submitted_at ON accessioning_submissions(submitted_at);')
            _conn.commit()
            _conn.close()
            logger.info("accessioning_submissions table verified/created")
    except Exception as _e:
        logger.warning(f"Schema migration warning: {_e}")

# Ensure instance directory exists (only for non-Vercel, non-Azure SQL environments)
if not USE_AZURE_SQL and env != 'vercel':
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    try:
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
    except Exception as e:
        logger.warning(f"Could not create instance directory: {e}")

    # Ensure session directory exists
    session_dir = os.path.join(instance_dir, 'flask_session')
    try:
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)
    except Exception as e:
        logger.warning(f"Could not create session directory: {e}")

# Initialize Flask-Session only if SESSION_TYPE is configured
# On Vercel, we use Flask's default signed cookie sessions
if app.config.get('SESSION_TYPE'):
    Session(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Flask-Mail
from services.email import mail
mail.init_app(app)

# Initialize security middleware (rate limiting and security headers)
from utils.security_middleware import setup_rate_limiting, setup_security_headers
limiter = setup_rate_limiting(app)
talisman = setup_security_headers(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Database path (for SQLite backward compatibility)
# When USE_AZURE_SQL is True, this is still set but models use db_connection module
DB_PATH = app.config.get('DATABASE_URI')

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    try:
        return User.get_by_id(DB_PATH, int(user_id))
    except Exception as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

# Import and register blueprints
from routes.auth import auth_bp
from routes.page1 import page1_bp
from routes.page2 import page2_bp
from routes.page3 import page3_bp
from routes.ypb_daily_count import ypb_bp
from routes.admin import admin_bp
from routes.export import export_bp
from routes.reports import reports_bp
from routes.accessioning import accessioning_bp

app.register_blueprint(auth_bp)
app.register_blueprint(page1_bp)
app.register_blueprint(page2_bp)
app.register_blueprint(page3_bp)
app.register_blueprint(ypb_bp)
app.register_blueprint(accessioning_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(export_bp, url_prefix='/export')
app.register_blueprint(reports_bp, url_prefix='/reports')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    from flask import render_template
    return render_template('error.html',
                         error_code=404,
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    from flask import render_template
    logger.error(f"Internal server error: {error}")
    return render_template('error.html',
                         error_code=500,
                         error_message='Internal server error'), 500

# Database error handler
@app.errorhandler(Exception)
def handle_database_error(error):
    from flask import render_template
    from werkzeug.exceptions import HTTPException

    # Let HTTP exceptions (404, 405, 400 CSRF, etc.) propagate normally
    if isinstance(error, HTTPException):
        return error

    # Check if this is a database connection error
    error_str = str(error).lower()
    if 'pymssql' in error_str or 'database' in error_str or 'connection' in error_str:
        logger.error(f"Database error: {error}")
        return render_template('error.html',
                             error_code=503,
                             error_message='Database connection error. Please try again later.'), 503

    raise error

# Context processor for global variables
@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    return {
        'app_name': 'Easy End of Shift',
        'use_azure_sql': USE_AZURE_SQL
    }

# Serve favicon at root path
@app.route('/favicon.svg')
def favicon():
    from flask import send_from_directory
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')

# Health check endpoint for Azure SQL
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    from flask import jsonify
    
    health_status = {
        'status': 'healthy',
        'database_mode': 'azure_sql' if USE_AZURE_SQL else 'sqlite',
        'timestamp': datetime.now().isoformat()
    }
    
    if USE_AZURE_SQL:
        try:
            from utils.db_connection import verify_all_connections
            results = verify_all_connections()
            health_status['databases'] = results
            if not all(results.values()):
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

# Validate configuration after app is configured
from utils.config_validator import validate_app_config
try:
    validate_app_config(app)
except RuntimeError as e:
    logger.critical(f"Configuration validation failed: {e}")
    raise

# For local development
if __name__ == '__main__':
    # Check if database exists (for SQLite mode), if not, provide instruction
    if not USE_AZURE_SQL and DB_PATH and not os.path.exists(DB_PATH):
        logger.warning("\n" + "="*60)
        logger.warning("WARNING: Database not found!")
        logger.warning("Please initialize the database first by running:")
        logger.warning("  python init_db.py")
        logger.warning("="*60 + "\n")

    logger.info("Starting development server on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
