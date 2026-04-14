"""
Audit logging utility for tracking user actions and system events
"""

import os
from datetime import datetime
from flask import request

# Database type detection
USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'

if USE_AZURE_SQL:
    import pymssql
else:
    import sqlite3


def get_connection(db_path):
    """
    Get database connection based on configuration
    Audit logs are stored in the ezeos database
    
    Args:
        db_path: For SQLite, this is the path. For Azure SQL, this is ignored.
        
    Returns:
        Database connection
    """
    if USE_AZURE_SQL:
        from utils.db_connection import get_ezeos_connection
        return get_ezeos_connection()
    else:
        return sqlite3.connect(db_path)


def log_action(db_path, user_id, action, table_name=None, record_id=None, details=None):
    """
    Log an action to the audit_log table
    
    Args:
        db_path: Path to the database (ignored for Azure SQL)
        user_id: ID of the user performing the action
        action: Description of the action (e.g., 'user_login', 'submission_created')
        table_name: Name of the table affected (optional)
        record_id: ID of the record affected (optional)
        details: Additional details as text (optional)
    """
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # Get IP address from request context
        ip_address = None
        try:
            ip_address = request.remote_addr if request else None
        except RuntimeError:
            # Outside of request context
            pass
        
        if USE_AZURE_SQL:
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, timestamp, ip_address, details)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, action, table_name, record_id, datetime.now(), ip_address, details))
        else:
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, table_name, record_id, timestamp, ip_address, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, action, table_name, record_id, datetime.now(), ip_address, details))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Audit log error: {e}")
        return False


def get_audit_logs(db_path, user_id=None, limit=100):
    """
    Retrieve audit logs with optional filtering
    
    Args:
        db_path: Path to the database (ignored for Azure SQL)
        user_id: Filter by user ID (optional)
        limit: Maximum number of records to return
        
    Returns:
        List of audit log records
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        if USE_AZURE_SQL:
            if user_id:
                cursor.execute('''
                    SELECT TOP (%s) id, user_id, action, table_name, record_id, timestamp, ip_address, details
                    FROM audit_log
                    WHERE user_id = %s
                    ORDER BY timestamp DESC
                ''', (limit, user_id))
            else:
                cursor.execute('''
                    SELECT TOP (%s) id, user_id, action, table_name, record_id, timestamp, ip_address, details
                    FROM audit_log
                    ORDER BY timestamp DESC
                ''', (limit,))
        else:
            if user_id:
                cursor.execute('''
                    SELECT id, user_id, action, table_name, record_id, timestamp, ip_address, details
                    FROM audit_log
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT id, user_id, action, table_name, record_id, timestamp, ip_address, details
                    FROM audit_log
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))
        
        results = cursor.fetchall()
        return results
    finally:
        conn.close()


def get_user_activity(db_path, user_id, days=30):
    """
    Get recent activity for a specific user
    
    Args:
        db_path: Path to the database (ignored for Azure SQL)
        user_id: User ID to query
        days: Number of days to look back
        
    Returns:
        List of recent actions
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        if USE_AZURE_SQL:
            cursor.execute('''
                SELECT action, timestamp, ip_address, details
                FROM audit_log
                WHERE user_id = %s
                AND timestamp >= DATEADD(day, -%s, GETDATE())
                ORDER BY timestamp DESC
            ''', (user_id, days))
        else:
            cursor.execute('''
                SELECT action, timestamp, ip_address, details
                FROM audit_log
                WHERE user_id = ?
                AND timestamp >= DATE('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            ''', (user_id, days))
        
        results = cursor.fetchall()
        return results
    finally:
        conn.close()
