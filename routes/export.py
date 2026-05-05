from flask import Blueprint, send_file, current_app, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models.submission import FormSubmission
from models.user import User
import csv
import io
from datetime import datetime

export_bp = Blueprint('export', __name__)

def admin_required(level=2):
    """Simple admin check for export routes"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            db_path = current_app.config['DATABASE_URI']
            admin_level = current_user.get_admin_level(db_path)
            
            if admin_level < level:
                flash('You do not have permission to export data.', 'error')
                return redirect(url_for('admin.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@export_bp.route('/csv')
@admin_required(level=2)
def export_csv():
    """Export submissions to CSV"""
    db_path = current_app.config['DATABASE_URI']
    
    # Get filters from request
    department = request.args.get('department', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    filters = {}
    if department:
        filters['department'] = department
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    # Get submissions
    submissions = FormSubmission.get_all(
        db_path, 
        limit=current_app.config['EXPORT_LIMIT'],
        filters=filters
    )
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Submission ID', 'User ID', 'Department', 'Login Timestamp',
        'Final Block Time', 'Baked IHCs PT Link', 'IHCs in PT Link',
        'Non-Baked IHC', 'IHCs in Buffer Wash', 'Pathologist Requests Status',
        'Request Source Email', 'Request Source Orchard', 'Request Source Send Out',
        'In Progress HER2', 'Upfront Special Stains', 'Peloris Maintenance',
        'Notes', 'Submitted At'
    ])
    
    # Write data
    for sub in submissions:
        writer.writerow([
            sub.id,
            sub.user_id,
            sub.department,
            sub.login_timestamp,
            sub.final_block_time or '',
            'Yes' if sub.baked_ihcs_pt_link else 'No',
            'Yes' if sub.ihcs_in_pt_link else 'No',
            'Yes' if sub.non_baked_ihc else 'No',
            'Yes' if sub.ihcs_in_buffer_wash else 'No',
            sub.pathologist_requests_status or '',
            'Yes' if sub.request_source_email else 'No',
            'Yes' if sub.request_source_orchard else 'No',
            'Yes' if sub.request_source_send_out else 'No',
            'Yes' if sub.in_progress_her2 else 'No',
            sub.upfront_special_stains or '',
            sub.peloris_maintenance or '',
            sub.notes or '',
            sub.submitted_at
        ])
    
    # Prepare file for download
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'lab_submissions_{timestamp}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@export_bp.route('/excel')
@admin_required(level=2)
def export_excel():
    """Export submissions to Excel (placeholder - requires openpyxl)"""
    flash('Excel export feature coming soon!', 'info')
    return redirect(url_for('admin.submissions'))

@export_bp.route('/pdf/<int:submission_id>')
@admin_required(level=2)
def export_pdf(submission_id):
    """Export single submission to PDF (placeholder - requires reportlab)"""
    flash('PDF export feature coming soon!', 'info')
    return redirect(url_for('admin.submission_detail', submission_id=submission_id))
