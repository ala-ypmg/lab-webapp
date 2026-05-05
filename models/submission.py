from datetime import datetime
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
    Submissions are stored in the main database

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


class FormSubmission:
    """Form submission model for storing completed workflow data"""
    
    def __init__(self, id=None, session_id=None, user_id=None,
                 login_timestamp=None, department=None, remember_me=False,
                 ypb_daily_count_data=None,
                 final_block_time=None, baked_ihcs_pt_link=None, ihcs_in_pt_link=None,
                 non_baked_ihc=None, ihcs_in_buffer_wash=None,
                 pathologist_requests_status=None, request_source_email=None,
                 request_source_orchard=None, request_source_send_out=None,
                 in_progress_her2=None,
                 upfront_special_stains=None, peloris_maintenance=None,
                 notes=None, submitted_at=None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        
        # Page 1 data
        self.login_timestamp = login_timestamp
        self.department = department
        self.remember_me = bool(remember_me) if remember_me is not None else False

        # Page 2 data (for Checkout department - YPB Daily Count)
        self.ypb_daily_count_data = ypb_daily_count_data

        # Page 2/3 data (workflow data)
        self.final_block_time = final_block_time
        self.baked_ihcs_pt_link = bool(baked_ihcs_pt_link) if baked_ihcs_pt_link is not None else None
        self.ihcs_in_pt_link = bool(ihcs_in_pt_link) if ihcs_in_pt_link is not None else None
        self.non_baked_ihc = bool(non_baked_ihc) if non_baked_ihc is not None else None
        self.ihcs_in_buffer_wash = bool(ihcs_in_buffer_wash) if ihcs_in_buffer_wash is not None else None
        self.pathologist_requests_status = pathologist_requests_status
        self.request_source_email = bool(request_source_email) if request_source_email is not None else None
        self.request_source_orchard = bool(request_source_orchard) if request_source_orchard is not None else None
        self.request_source_send_out = bool(request_source_send_out) if request_source_send_out is not None else None
        self.in_progress_her2 = bool(in_progress_her2) if in_progress_her2 is not None else None
        self.upfront_special_stains = upfront_special_stains
        self.peloris_maintenance = peloris_maintenance

        # Page 3/4 data (notes)
        self.notes = notes
        
        self.submitted_at = submitted_at or datetime.now()
    
    @staticmethod
    def create_from_session(db_path, session):
        """Create a submission record from a completed session"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT INTO form_submissions (
                    session_id, user_id,
                    login_timestamp, department, remember_me,
                    ypb_daily_count_data,
                    final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                    non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                    request_source_email, request_source_orchard, request_source_send_out,
                    in_progress_her2, upfront_special_stains, peloris_maintenance,
                    notes, submitted_at
                ) VALUES ({PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH})
            ''', (
                session.id, session.user_id,
                session.login_timestamp, session.department, bool_to_db(session.remember_me),
                session.ypb_daily_count_data,
                session.final_block_time, 
                bool_to_db(session.baked_ihcs_pt_link), 
                bool_to_db(session.ihcs_in_pt_link),
                bool_to_db(session.non_baked_ihc), 
                bool_to_db(session.ihcs_in_buffer_wash),
                session.pathologist_requests_status, 
                bool_to_db(session.request_source_email),
                bool_to_db(session.request_source_orchard), 
                bool_to_db(session.request_source_send_out),
                bool_to_db(session.in_progress_her2),
                session.upfront_special_stains, session.peloris_maintenance,
                session.notes, datetime.now()
            ))
            
            conn.commit()
            submission_id = get_lastrowid(cursor)
            
            return FormSubmission.get_by_id(db_path, submission_id)
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(db_path, submission_id):
        """Get submission by ID"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'''
                SELECT id, session_id, user_id,
                       login_timestamp, department, remember_me,
                       ypb_daily_count_data,
                       final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                       non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                       request_source_email, request_source_orchard, request_source_send_out,
                       in_progress_her2, upfront_special_stains, peloris_maintenance,
                       notes, submitted_at
                FROM form_submissions WHERE id = {PH}
            ''', (submission_id,))
            result = cursor.fetchone()
            
            if result:
                return FormSubmission(*result)
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_all(db_path, limit=None, offset=0, filters=None):
        """Get all submissions with optional filters and pagination"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # Base query
        base_columns = '''
            SELECT id, session_id, user_id,
                   login_timestamp, department, remember_me,
                   ypb_daily_count_data,
                   final_block_time, baked_ihcs_pt_link, ihcs_in_pt_link,
                   non_baked_ihc, ihcs_in_buffer_wash, pathologist_requests_status,
                   request_source_email, request_source_orchard, request_source_send_out,
                   in_progress_her2, upfront_special_stains, peloris_maintenance,
                   notes, submitted_at
            FROM form_submissions
        '''
        
        params = []
        where_clauses = []
        
        if filters:
            if filters.get('session_id'):
                where_clauses.append(f'session_id = {PH}')
                params.append(filters['session_id'])

            if filters.get('department'):
                where_clauses.append(f'department = {PH}')
                params.append(filters['department'])

            if filters.get('start_date'):
                where_clauses.append(f'submitted_at >= {PH}')
                params.append(filters['start_date'])

            if filters.get('end_date'):
                where_clauses.append(f'submitted_at <= {PH}')
                params.append(filters['end_date'])

            if filters.get('user_id'):
                where_clauses.append(f'user_id = {PH}')
                params.append(filters['user_id'])

        where_clause = ''
        if where_clauses:
            where_clause = ' WHERE ' + ' AND '.join(where_clauses)

        try:
            if USE_AZURE_SQL:
                # SQL Server uses OFFSET/FETCH NEXT for pagination
                query = base_columns + where_clause + ' ORDER BY submitted_at DESC'

                if limit:
                    query += ' OFFSET %s ROWS FETCH NEXT %s ROWS ONLY'
                    params.extend([offset, limit])
                
                cursor.execute(query, params)
            else:
                # SQLite uses LIMIT/OFFSET
                query = base_columns + where_clause + ' ORDER BY submitted_at DESC'
                
                if limit:
                    query += ' LIMIT ? OFFSET ?'
                    params.extend([limit, offset])
                
                cursor.execute(query, params)
            
            results = cursor.fetchall()
            
            return [FormSubmission(*result) for result in results]
        finally:
            conn.close()
    
    @staticmethod
    def get_count(db_path, filters=None):
        """Get total count of submissions with optional filters"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        query = 'SELECT COUNT(*) FROM form_submissions'
        params = []
        where_clauses = []
        
        if filters:
            if filters.get('session_id'):
                where_clauses.append(f'session_id = {PH}')
                params.append(filters['session_id'])

            if filters.get('department'):
                where_clauses.append(f'department = {PH}')
                params.append(filters['department'])

            if filters.get('start_date'):
                where_clauses.append(f'submitted_at >= {PH}')
                params.append(filters['start_date'])

            if filters.get('end_date'):
                where_clauses.append(f'submitted_at <= {PH}')
                params.append(filters['end_date'])

            if filters.get('user_id'):
                where_clauses.append(f'user_id = {PH}')
                params.append(filters['user_id'])
        
        if where_clauses:
            query += ' WHERE ' + ' AND '.join(where_clauses)
        
        try:
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            return count
        finally:
            conn.close()
    
    @staticmethod
    def get_by_department(db_path, department):
        """Get all submissions for a specific department"""
        return FormSubmission.get_all(db_path, filters={'department': department})
    
    @staticmethod
    def get_by_user(db_path, user_id):
        """Get all submissions by a specific user"""
        return FormSubmission.get_all(db_path, filters={'user_id': user_id})
    
    @staticmethod
    def get_recent(db_path, days=30, limit=100):
        """Get recent submissions within specified days"""
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        return FormSubmission.get_all(
            db_path, 
            limit=limit,
            filters={'start_date': start_date.strftime('%Y-%m-%d')}
        )
    
    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
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
            'submitted_at': self.submitted_at,
            'ypb_daily_count_data': self.ypb_daily_count_data
        }
    
    def delete(self, db_path):
        """Delete submission (soft delete - should be logged in audit)"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f'DELETE FROM form_submissions WHERE id = {PH}', (self.id,))
            conn.commit()
        finally:
            conn.close()
