import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database - SQLite (legacy, for backward compatibility)
    DATABASE_URI = os.path.join(os.path.dirname(__file__), 'instance', 'lab_data.db')
    
    # Azure SQL Configuration
    USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'
    AZURE_SQL_SERVER = os.environ.get('AZURE_SQL_SERVER', 'ezeos.database.windows.net')
    AZURE_SQL_USERNAME = os.environ.get('AZURE_SQL_USERNAME', 'ala')
    AZURE_SQL_PASSWORD = os.environ.get('AZURE_SQL_PASSWORD', '')
    AZURE_SQL_DATABASE_USERS = os.environ.get('AZURE_SQL_DATABASE_USERS', 'users')
    AZURE_SQL_DATABASE_MAIN = os.environ.get('AZURE_SQL_DATABASE_MAIN', 'main')
    
    # Session Management
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'instance', 'flask_session')
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Remember Me
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    
    # Admin Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@ypmg.com')
    EXPORT_LIMIT = 10000  # Max rows per export
    REPORT_CACHE_TTL = 300  # 5 minutes cache
    ENABLE_AUDIT_LOG = True
    ITEMS_PER_PAGE = 50  # Pagination
    
    # WTForms
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # File Upload (for future features)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # EMAIL CONFIGURATION (Microsoft 365)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.office365.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # REGISTRATION SETTINGS
    ALLOWED_EMAIL_DOMAIN = os.environ.get('ALLOWED_EMAIL_DOMAIN', 'ypmg.com')
    CONFIRMATION_TOKEN_EXPIRY = int(os.environ.get('CONFIRMATION_TOKEN_EXPIRY', 3600))
    
    @classmethod
    def get_azure_connection_params(cls, database='users'):
        """
        Build pymssql connection keyword arguments for Azure SQL.

        Args:
            database: Which database to connect to ('users' or 'main')

        Returns:
            dict of keyword arguments for pymssql.connect()
        """
        if database == 'users':
            db_name = cls.AZURE_SQL_DATABASE_USERS
        else:
            db_name = cls.AZURE_SQL_DATABASE_MAIN

        return {
            'server': cls.AZURE_SQL_SERVER,
            'user': cls.AZURE_SQL_USERNAME,
            'password': cls.AZURE_SQL_PASSWORD,
            'database': db_name,
            'tds_version': '7.4',
            'login_timeout': 30,
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    # Use SQLite by default in development
    USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    REMEMBER_COOKIE_SECURE = True  # Enable for HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Use Azure SQL in production
    USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'true').lower() == 'true'
    SESSION_TYPE = None
    SESSION_FILE_DIR = None

class AzureSQLConfig(ProductionConfig):
    """Azure SQL production configuration"""
    USE_AZURE_SQL = True
    # Override DATABASE_URI to indicate Azure SQL is in use
    DATABASE_URI = None  # Not used with Azure SQL

class VercelConfig(ProductionConfig):
    """Vercel serverless configuration"""
    # Use Flask's default signed cookie sessions (no server-side storage)
    # This is necessary because Vercel's filesystem is read-only except /tmp
    SESSION_TYPE = None  # Don't use Flask-Session, fall back to Flask's default
    SESSION_FILE_DIR = None  # Not needed for cookie sessions
    
    # Use /tmp for database (writable on Vercel)
    DATABASE_URI = '/tmp/lab_data.db'
    # Vercel typically uses Azure SQL in production
    USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_URI = ':memory:'  # In-memory database for testing
    MAIL_SUPPRESS_SEND = True
    USE_AZURE_SQL = False  # Always use SQLite for testing

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'azure_sql': AzureSQLConfig,
    'vercel': VercelConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
