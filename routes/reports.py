from flask import Blueprint, render_template, current_app, jsonify
from flask_login import login_required, current_user
from models.submission import FormSubmission
import sqlite3
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

def admin_required(level=1):
    """Simple admin check for reports routes"""
    from functools import wraps
    from flask import flash, redirect, url_for
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            db_path = current_app.config['DATABASE_URI']
            admin_level = current_user.get_admin_level(db_path)
            
            if admin_level < level:
                flash('You do not have permission to view reports.', 'error')
                return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@reports_bp.route('/')
@admin_required(level=1)
def index():
    """Main reports page"""
    return render_template('admin/reports.html')

@reports_bp.route('/summary')
@admin_required(level=1)
def summary():
    """Summary statistics report"""
    db_path = current_app.config['DATABASE_URI']
    
    # Get total submissions
    total = FormSubmission.get_count(db_path)
    
    # Get recent submissions (last 30 days)
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_count = FormSubmission.get_count(db_path, filters={'start_date': start_date})
    
    # Get department breakdown
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT department, COUNT(*) as count
        FROM form_submissions
        GROUP BY department
        ORDER BY count DESC
    ''')
    dept_breakdown = cursor.fetchall()
    conn.close()
    
    stats = {
        'total_submissions': total,
        'recent_submissions': recent_count,
        'department_breakdown': dept_breakdown
    }
    
    return render_template('admin/summary_report.html', stats=stats)

@reports_bp.route('/department')
@admin_required(level=1)
def department():
    """Department-wise report"""
    db_path = current_app.config['DATABASE_URI']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get department statistics
    cursor.execute('''
        SELECT 
            department,
            COUNT(*) as total,
            COUNT(CASE WHEN submitted_at >= DATE('now', '-7 days') THEN 1 END) as week,
            COUNT(CASE WHEN submitted_at >= DATE('now', '-30 days') THEN 1 END) as month
        FROM form_submissions
        GROUP BY department
        ORDER BY total DESC
    ''')
    
    dept_stats = cursor.fetchall()
    conn.close()
    
    return render_template('admin/department_report.html', departments=dept_stats)

@reports_bp.route('/trends')
@admin_required(level=1)
def trends():
    """Time-based trends analysis"""
    db_path = current_app.config['DATABASE_URI']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get daily submission counts for last 30 days
    cursor.execute('''
        SELECT DATE(submitted_at) as date, COUNT(*) as count
        FROM form_submissions
        WHERE submitted_at >= DATE('now', '-30 days')
        GROUP BY DATE(submitted_at)
        ORDER BY date
    ''')
    
    daily_trends = cursor.fetchall()
    conn.close()
    
    return render_template('admin/trends_report.html', trends=daily_trends)

@reports_bp.route('/api/data')
@admin_required(level=1)
def api_data():
    """JSON API for chart data"""
    db_path = current_app.config['DATABASE_URI']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get last 30 days data
    cursor.execute('''
        SELECT DATE(submitted_at) as date, COUNT(*) as count
        FROM form_submissions
        WHERE submitted_at >= DATE('now', '-30 days')
        GROUP BY DATE(submitted_at)
        ORDER BY date
    ''')
    
    timeline_data = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Get department distribution
    cursor.execute('''
        SELECT department, COUNT(*) as count
        FROM form_submissions
        GROUP BY department
    ''')
    
    dept_data = [{'department': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'timeline': timeline_data,
        'departments': dept_data
    })
