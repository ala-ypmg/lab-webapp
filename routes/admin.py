from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from models.user import User
from models.submission import FormSubmission
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)

def admin_required(level=1):
    """Decorator to require admin privileges"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            db_path = current_app.config['DATABASE_URI']
            admin_level = current_user.get_admin_level(db_path)
            
            if admin_level < level:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin_bp.route('/')
@admin_required(level=1)
def dashboard():
    """Admin dashboard with analytics and quick stats"""
    db_path = current_app.config['DATABASE_URI']
    
    # Get statistics
    total_submissions = FormSubmission.get_count(db_path)
    recent_submissions = FormSubmission.get_recent(db_path, days=30, limit=10)
    
    # Get all users (for admin level 3+)
    users = []
    if current_user.get_admin_level(db_path) >= 3:
        users = User.get_all_users(db_path)
    
    stats = {
        'total_submissions': total_submissions,
        'recent_count': len(recent_submissions),
        'total_users': len(users) if users else 0
    }
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_submissions=recent_submissions,
                         admin_level=current_user.get_admin_level(db_path))

@admin_bp.route('/users')
@admin_required(level=3)
def users():
    """User management page (admin level 3 required)"""
    db_path = current_app.config['DATABASE_URI']
    all_users = User.get_all_users(db_path)
    
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/submissions')
@admin_required(level=2)
def submissions():
    """Browse all submissions (admin level 2 required)"""
    db_path = current_app.config['DATABASE_URI']
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    # Get filters
    department = request.args.get('department', '')
    
    filters = {}
    if department:
        filters['department'] = department
    
    # Get submissions
    offset = (page - 1) * per_page
    submissions_list = FormSubmission.get_all(db_path, limit=per_page, offset=offset, filters=filters)
    total = FormSubmission.get_count(db_path, filters=filters)
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return render_template('admin/submissions.html',
                         submissions=submissions_list,
                         page=page,
                         total_pages=total_pages,
                         total=total)

@admin_bp.route('/submissions/<int:submission_id>')
@admin_required(level=2)
def submission_detail(submission_id):
    """View specific submission details"""
    db_path = current_app.config['DATABASE_URI']
    submission = FormSubmission.get_by_id(db_path, submission_id)
    
    if not submission:
        flash('Submission not found.', 'error')
        return redirect(url_for('admin.submissions'))
    
    return render_template('admin/submission_detail.html', submission=submission)

@admin_bp.route('/users/create', methods=['POST'])
@admin_required(level=3)
def create_user():
    """Create a new user (admin level 3 required)"""
    db_path = current_app.config['DATABASE_URI']

    user_id = request.form.get('user_id')
    email = request.form.get('email')
    passcode = request.form.get('passcode')

    if not user_id or not email or not passcode:
        flash('User ID, email, and passcode are required.', 'error')
        return redirect(url_for('admin.users'))

    # Validate passcode is 4 digits
    if not passcode.isdigit() or len(passcode) != 4:
        flash('Passcode must be exactly 4 digits.', 'error')
        return redirect(url_for('admin.users'))

    # Create user with proper signature: create(db_path, user_id, email, passcode)
    user = User.create(db_path, user_id, email, passcode)

    if user:
        logger.info(f"Admin {current_user.user_id} created new user: {user_id}")
        flash(f'User {user_id} created successfully.', 'success')
    else:
        logger.warning(f"Failed to create user {user_id} - already exists")
        flash(f'User {user_id} already exists.', 'error')

    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required(level=3)
def deactivate_user(user_id):
    """Deactivate a user account"""
    db_path = current_app.config['DATABASE_URI']
    user = User.get_by_id(db_path, user_id)

    if user:
        user.deactivate(db_path)
        logger.info(f"Admin {current_user.user_id} deactivated user: {user.user_id}")
        flash(f'User {user.user_id} has been deactivated.', 'success')
    else:
        logger.warning(f"Attempt to deactivate non-existent user ID: {user_id}")
        flash('User not found.', 'error')

    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required(level=3)
def activate_user(user_id):
    """Activate a user account"""
    db_path = current_app.config['DATABASE_URI']
    user = User.get_by_id(db_path, user_id)

    if user:
        user.activate(db_path)
        logger.info(f"Admin {current_user.user_id} activated user: {user.user_id}")
        flash(f'User {user.user_id} has been activated.', 'success')
    else:
        logger.warning(f"Attempt to activate non-existent user ID: {user_id}")
        flash('User not found.', 'error')

    return redirect(url_for('admin.users'))
