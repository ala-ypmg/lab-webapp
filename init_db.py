import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize the database with all required tables"""
    
    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    
    db_path = os.path.join(instance_dir, 'lab_data.db')
    
    # Connect to database
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
            
            -- Page 1 data (stored immediately on login)
            login_timestamp TIMESTAMP,
            department VARCHAR(50),
            remember_me BOOLEAN DEFAULT 0,
            
            -- Page 2 data (stored when page 2 is submitted)
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
            
            -- Page 3 data (stored when page 3 is submitted)
            notes TEXT,
            
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create Form Submissions table (final complete submissions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS form_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            
            -- Page 1 Data
            login_timestamp TIMESTAMP NOT NULL,
            department VARCHAR(50) NOT NULL,
            remember_me BOOLEAN DEFAULT 0,
            
            -- Page 2 Data
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
            
            -- Page 3 Data
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

    # Create indexes for better performance
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
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at: {db_path}")
    print("Tables created:")
    print("  - users")
    print("  - user_sessions")
    print("  - form_submissions")
    print("  - admin_users")
    print("  - audit_log")
    print("  - accessioning_submissions")

if __name__ == '__main__':
    init_database()
