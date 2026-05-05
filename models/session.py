from datetime import datetime
import secrets
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
    Sessions are stored in the main database

    Args:
        db_path: For SQLite, this is the path. For Azure SQL, this is ignored.

    Returns:
        Database connection
    """
    if USE_AZURE_SQL:
        from utils.db_connection import get_main_connection
        return get_main_connection()
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


def bool_to_db(value):
    """Convert Python boolean to database value (1/0)"""
    if value is None:
        return None
    return 1 if value else 0


_VALID_STATUSES = {'done', 'pending', 'na'}


def _coerce_status(value):
    """Coerce a workflow status field to 'done'/'pending'/'na' or None.

    Old sessions stored 1/0 integers; new sessions store strings.
    Any non-string truthy legacy value maps to 'done'.
    """
    if value is None:
        return None
    if isinstance(value, str):
        if value in _VALID_STATUSES:
            return value
        # Legacy: BIT→NVARCHAR migration leaves '1'/'0' strings in old rows
        return 'done' if value == '1' else None
    # Legacy integer: 1 → 'done', 0 → None
    return 'done' if value else None


class UserSession:
    """User session model for tracking workflow progress"""
    
    def __init__(self, id=None, session_id=None, user_id=None, current_page=1,
                 max_page_reached=1, started_at=None, completed=False,
                 login_timestamp=None, department=None, remember_me=False,
                 ypb_daily_count_data=None,
                 final_block_time=None, baked_ihcs_pt_link=None, ihcs_in_pt_link=None,
                 non_baked_ihc=None, ihcs_in_buffer_wash=None,
                 pathologist_requests_status=None, request_source_email=None,
                 request_source_orchard=None, request_source_send_out=None,
                 in_progress_her2=None,
                 upfront_special_stains=None, peloris_maintenance=None, notes=None):
        self.id = id
        self.session_id = session_id or self.generate_session_id()
        self.user_id = user_id
        self.current_page = current_page
        self.max_page_reached = max_page_reached
        self.started_at = started_at or datetime.now()
        self.completed = bool(completed) if completed is not None else False
        
        # Page 1 data
        self.login_timestamp = login_timestamp
        self.department = department
        self.remember_me = bool(remember_me) if remember_me is not None else False

        # Page 2 data (for Checkout department - YPB Daily Count)
        self.ypb_daily_count_data = ypb_daily_count_data

        # Page 2/3 data (workflow data)
        self.final_block_time = final_block_time
        # Status fields store 'done'/'pending'/'na' strings (or None)
        self.baked_ihcs_pt_link = _coerce_status(baked_ihcs_pt_link)
        self.ihcs_in_pt_link = _coerce_status(ihcs_in_pt_link)
        self.non_baked_ihc = _coerce_status(non_baked_ihc)
        self.ihcs_in_buffer_wash = _coerce_status(ihcs_in_buffer_wash)
        self.pathologist_requests_status = _coerce_status(pathologist_requests_status)
        self.request_source_email = bool(request_source_email) if request_source_email is not None else None
        self.request_source_orchard = bool(request_source_orchard) if request_source_orchard is not None else None
        self.request_source_send_out = bool(request_source_send_out) if request_source_send_out is not None else None
        self.in_progress_her2 = _coerce_status(in_progress_her2)
        self.upfront_special_stains = _coerce_status(upfront_special_stains)
        self.peloris_maintenance = _coerce_status(peloris_maintenance)

        # Page 3/4 data (notes)
        self.notes = notes
    
    @staticmethod
    def generate_session_id():
        """Generate a secure random session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create(db_path, user_id, login_timestamp, department, remember_me=False):
        """Create a new session"""
        session = UserSession(
            user_id=user_id,
            login_timestamp=login_timestamp,
            department=department,
            remember_me=remember_me
        )
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                INSERT INTO user_sessions (
                    session_id, user_id, current_page, max_page_reached,
                    started_at, completed, login_timestamp, department, remember_me
                ) VALUES ({PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH})
            ''', (session.session_id, user_id, 1, 1, session.started_at,
                  bool_to_db(False), login_timestamp, department, bool_to_db(remember_me)))
            conn.commit()
            session.id = get_lastrowid(cursor)
            return session
        finally:
            conn.close()
    
    @staticmethod
    def get_by_session_id(db_path, session_id):
        """Get session by session_id"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT id, session_id, user_id, current_page, max_page_reached,
                       started_at, completed, login_timestamp, department, remember_me,
                       ypb_daily_count_data,
                       final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                       non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                       request_source_email, request_source_orchard, request_source_send_out,
                       in_progress_her2, upfront_special_stains, peloris_maintenance, notes
                FROM user_sessions WHERE session_id = {PH}
            ''', (session_id,))
            result = cursor.fetchone()
            
            if result:
                return UserSession(*result)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_active_session(db_path, user_id):
        """Get active (incomplete) session for user"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            if USE_AZURE_SQL:
                # SQL Server uses TOP 1 instead of LIMIT 1
                cursor.execute('''
                    SELECT TOP 1 id, session_id, user_id, current_page, max_page_reached,
                           started_at, completed, login_timestamp, department, remember_me,
                           ypb_daily_count_data,
                           final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                           non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                           request_source_email, request_source_orchard, request_source_send_out,
                           in_progress_her2, upfront_special_stains, peloris_maintenance, notes
                    FROM user_sessions
                    WHERE user_id = %s AND completed = 0
                    ORDER BY started_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, session_id, user_id, current_page, max_page_reached,
                           started_at, completed, login_timestamp, department, remember_me,
                           ypb_daily_count_data,
                           final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                           non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                           request_source_email, request_source_orchard, request_source_send_out,
                           in_progress_her2, upfront_special_stains, peloris_maintenance, notes
                    FROM user_sessions
                    WHERE user_id = ? AND completed = 0
                    ORDER BY started_at DESC LIMIT 1
                ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                return UserSession(*result)
            return None
        finally:
            conn.close()
    
    def update_page(self, db_path, page_number):
        """Update current page and max_page_reached"""
        self.current_page = page_number
        if page_number > self.max_page_reached:
            self.max_page_reached = page_number
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE user_sessions
                SET current_page = {PH}, max_page_reached = {PH}
                WHERE id = {PH}
            ''', (self.current_page, self.max_page_reached, self.id))
            conn.commit()
        finally:
            conn.close()
    
    def save_ypb_data(self, db_path, ypb_data_json):
        """Save YPB Daily Count data (Page 2 for Checkout department)"""
        self.ypb_daily_count_data = ypb_data_json

        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE user_sessions SET ypb_daily_count_data = {PH} WHERE id = {PH}
            ''', (ypb_data_json, self.id))
            conn.commit()
        finally:
            conn.close()

    def save_page2_data(self, db_path, data):
        """Save Page 2/3 workflow data (depending on department)"""
        self.final_block_time = data.get('final_block_time')
        self.baked_ihcs_pt_link = data.get('baked_ihcs_pt_link')
        self.ihcs_in_pt_link = data.get('ihcs_in_pt_link')
        self.non_baked_ihc = data.get('non_baked_ihc')
        self.ihcs_in_buffer_wash = data.get('ihcs_in_buffer_wash')
        self.pathologist_requests_status = data.get('pathologist_requests_status')
        self.request_source_email = data.get('request_source_email', False)
        self.request_source_orchard = data.get('request_source_orchard', False)
        self.request_source_send_out = data.get('request_source_send_out', False)
        self.in_progress_her2 = data.get('in_progress_her2')
        self.upfront_special_stains = data.get('upfront_special_stains')
        self.peloris_maintenance = data.get('peloris_maintenance')

        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE user_sessions SET
                    final_block_time = {PH},
                    baked_ihcs_pt_link = {PH},
                    ihcs_in_pt_link = {PH},
                    non_baked_ihc = {PH},
                    ihcs_in_buffer_wash = {PH},
                    pathologist_requests_status = {PH},
                    request_source_email = {PH},
                    request_source_orchard = {PH},
                    request_source_send_out = {PH},
                    in_progress_her2 = {PH},
                    upfront_special_stains = {PH},
                    peloris_maintenance = {PH}
                WHERE id = {PH}
            ''', (self.final_block_time,
                  self.baked_ihcs_pt_link,
                  self.ihcs_in_pt_link,
                  self.non_baked_ihc,
                  self.ihcs_in_buffer_wash,
                  self.pathologist_requests_status,
                  bool_to_db(self.request_source_email),
                  bool_to_db(self.request_source_orchard),
                  bool_to_db(self.request_source_send_out),
                  self.in_progress_her2,
                  self.upfront_special_stains,
                  self.peloris_maintenance,
                  self.id))
            conn.commit()
        finally:
            conn.close()
    
    def save_page3_data(self, db_path, notes):
        """Save Page 3/4 notes data (depending on department)"""
        self.notes = notes
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE user_sessions SET notes = {PH} WHERE id = {PH}
            ''', (notes, self.id))
            conn.commit()
        finally:
            conn.close()
    
    def mark_completed(self, db_path):
        """Mark session as completed"""
        self.completed = True
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                UPDATE user_sessions SET completed = 1 WHERE id = {PH}
            ''', (self.id,))
            conn.commit()
        finally:
            conn.close()
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'current_page': self.current_page,
            'max_page_reached': self.max_page_reached,
            'started_at': self.started_at,
            'completed': self.completed,
            'login_timestamp': self.login_timestamp,
            'department': self.department,
            'remember_me': self.remember_me,
            'final_block_time': self.final_block_time,
            'baked_ihcs_pt_link': self.baked_ihcs_pt_link,
            'ihcs_in_pt_link': self.ihcs_in_pt_link,
            'non_baked_ihc': self.non_baked_ihc,
            'ihcs_in_buffer_wash': self.ihcs_in_buffer_wash,
            'pathologist_requests_status': self.pathologist_requests_status,
            'request_source_email': self.request_source_email,
            'request_source_orchard': self.request_source_orchard,
            'request_source_send_out': self.request_source_send_out,
            'in_progress_her2': self.in_progress_her2,
            'upfront_special_stains': self.upfront_special_stains,
            'peloris_maintenance': self.peloris_maintenance,
            'notes': self.notes,
            'ypb_daily_count_data': self.ypb_daily_count_data
        }
