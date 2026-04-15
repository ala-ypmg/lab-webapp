#!/usr/bin/env python3
"""
Migration script to add ypb_daily_count_data column to user_sessions and form_submissions tables
"""

import sqlite3
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config

def add_ypb_daily_count_column():
    """Add ypb_daily_count_data column to database tables"""

    # Get database path
    env = os.environ.get('FLASK_ENV', 'production')
    db_path = config[env].DATABASE_URI

    print(f"Connecting to database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists in user_sessions
        cursor.execute("PRAGMA table_info(user_sessions)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'ypb_daily_count_data' not in columns:
            print("Adding ypb_daily_count_data column to user_sessions table...")
            cursor.execute('''
                ALTER TABLE user_sessions
                ADD COLUMN ypb_daily_count_data TEXT
            ''')
            print("✓ Column added to user_sessions")
        else:
            print("✓ Column already exists in user_sessions")

        # Check if column already exists in form_submissions
        cursor.execute("PRAGMA table_info(form_submissions)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'ypb_daily_count_data' not in columns:
            print("Adding ypb_daily_count_data column to form_submissions table...")
            cursor.execute('''
                ALTER TABLE form_submissions
                ADD COLUMN ypb_daily_count_data TEXT
            ''')
            print("✓ Column added to form_submissions")
        else:
            print("✓ Column already exists in form_submissions")

        conn.commit()
        print("\n✓ Migration completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during migration: {e}")
        conn.rollback()
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    add_ypb_daily_count_column()
