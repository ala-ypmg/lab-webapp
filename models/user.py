from flask_login import UserMixin
from datetime import datetime
import bcrypt
import os

# Database type detection
USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'
PH = '%s' if USE_AZURE_SQL else '?'

if USE_AZURE_SQL:
    import pymssql
else:
    import sqlite3


def get_connection(db_path):
    """
    Get database connection based on configuration
    
    Args:
        db_path: For SQLite, this is the path. For Azure SQL, this is ignored.
        
    Returns:
        Database connection
    """
    if USE_AZURE_SQL:
        from utils.db_connection import get_users_connection
        return get_users_connection()
    else:
        return sqlite3.connect(db_path)


def get_lastrowid(cursor):
    """Get last inserted row ID"""
    if USE_AZURE_SQL:
        cursor.execute("SELECT SCOPE_IDENTITY()")
        result = cursor.fetchone()
        return int(result[0]) if result and result[0] else None
    else:
        return cursor.lastrowid


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, id, user_id, email, passcode_hash, created_at=None, last_login=None,
                 is_active=True, is_confirmed=False, confirmed_at=None):
        self.id = id
        self.user_id = user_id
        self.email = email
        self.passcode_hash = passcode_hash
        self.created_at = created_at
        self.last_login = last_login
        # Use private attribute to store is_active value
        self._is_active = bool(is_active) if is_active is not None else True
        self.is_confirmed = bool(is_confirmed) if is_confirmed is not None else False
        self.confirmed_at = confirmed_at
    
    @property
    def is_active(self):
        """Override UserMixin's is_active property to make it settable"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """Allow setting is_active value"""
        self._is_active = bool(value) if value is not None else True
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    def check_passcode(self, passcode):
        """Verify passcode against hash"""
        return bcrypt.checkpw(passcode.encode('utf-8'), self.passcode_hash.encode('utf-8'))
    
    @staticmethod
    def hash_passcode(passcode):
        """Hash a passcode using bcrypt"""
        return bcrypt.hashpw(passcode.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def get_by_id(db_path, user_id):
        """Get user by ID from database"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT id, user_id, email, passcode_hash, created_at, last_login,
                       is_active, is_confirmed, confirmed_at
                FROM users WHERE id = {PH}
            ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return User(*result)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user_id(db_path, user_id):
        """Get user by user_id (username) from database"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            if USE_AZURE_SQL:
                cursor.execute('''
                    SELECT id, user_id, email, passcode_hash, created_at, last_login,
                           is_active, is_confirmed, confirmed_at
                    FROM users WHERE LOWER(user_id) = LOWER(%s)
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, user_id, email, passcode_hash, created_at, last_login,
                           is_active, is_confirmed, confirmed_at
                    FROM users WHERE LOWER(user_id) = LOWER(?)
                ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return User(*result)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def create(db_path, user_id, email, passcode):
        """Create a new user"""
        passcode_hash = User.hash_passcode(passcode)
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT INTO users (user_id, email, passcode_hash, created_at, is_confirmed)
                VALUES ({PH}, {PH}, {PH}, {PH}, 0)
            ''', (user_id, email.lower(), passcode_hash, datetime.now()))
            conn.commit()
            new_id = get_lastrowid(cursor)
            return User.get_by_id(db_path, new_id)
        except (sqlite3.IntegrityError if not USE_AZURE_SQL else pymssql.IntegrityError):
            return None  # User already exists
        except Exception as e:
            # Handle Azure SQL unique constraint violation
            if USE_AZURE_SQL and 'UNIQUE' in str(e).upper():
                return None
            raise
        finally:
            conn.close()
    
    def update_last_login(self, db_path):
        """Update last login timestamp"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE users SET last_login = {PH} WHERE id = {PH}
            ''', (datetime.now(), self.id))
            conn.commit()
            self.last_login = datetime.now()
        finally:
            conn.close()
    
    def is_admin(self, db_path):
        """Check if user has admin privileges"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT admin_level FROM admin_users WHERE user_id = {PH}
            ''', (self.id,))
            result = cursor.fetchone()
            return result is not None
        finally:
            conn.close()

    def get_admin_level(self, db_path):
        """Get admin level (1, 2, or 3). Returns 0 if not admin"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT admin_level FROM admin_users WHERE user_id = {PH}
            ''', (self.id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            conn.close()
    
    @staticmethod
    def get_all_users(db_path):
        """Get all users (for admin panel)"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, user_id, email, passcode_hash, created_at, last_login,
                       is_active, is_confirmed, confirmed_at
                FROM users
                ORDER BY created_at DESC
            ''')
            results = cursor.fetchall()
            
            return [User(*result) for result in results]
        finally:
            conn.close()
    
    @staticmethod
    def get_by_email(db_path, email):
        """Get user by email from database"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT id, user_id, email, passcode_hash, created_at, last_login,
                       is_active, is_confirmed, confirmed_at
                FROM users WHERE LOWER(email) = LOWER({PH})
            ''', (email,))
            result = cursor.fetchone()
            
            if result:
                return User(*result)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def is_valid_email_domain(email, allowed_domain='ypmg.com'):
        """Validate email domain"""
        if not email or '@' not in email:
            return False
        domain = email.lower().split('@')[-1]
        return domain == allowed_domain.lower()
    
    def confirm_email(self, db_path):
        """Confirm user email"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE users SET is_confirmed = 1, confirmed_at = {PH} WHERE id = {PH}
            ''', (datetime.now(), self.id))
            conn.commit()
            self.is_confirmed = True
            self.confirmed_at = datetime.now()
        finally:
            conn.close()
    
    def deactivate(self, db_path):
        """Deactivate user account"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'UPDATE users SET is_active = 0 WHERE id = {PH}', (self.id,))
            conn.commit()
            self.is_active = False
        finally:
            conn.close()
    
    def activate(self, db_path):
        """Activate user account"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'UPDATE users SET is_active = 1 WHERE id = {PH}', (self.id,))
            conn.commit()
            self.is_active = True
        finally:
            conn.close()
