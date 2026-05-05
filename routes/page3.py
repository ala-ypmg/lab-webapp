from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session as flask_session
from flask_login import login_required, current_user
from forms.notes_form import NotesForm
from models.session import UserSession
from models.submission import FormSubmission
from datetime import datetime

page3_bp = Blueprint('page3', __name__)

@page3_bp.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    """Page 3/4 - Notes Entry and Final Submission (Page 3 for non-Checkout, Page 4 for Checkout)"""
    db_path = current_app.config['DATABASE_URI']

    # Get or validate session
    session_id = flask_session.get('workflow_session_id')
    if not session_id:
        flash('Session not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    user_session = UserSession.get_by_session_id(db_path, session_id)

    if not user_session or user_session.user_id != current_user.id:
        flash('Invalid session. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    # Check if session is completed
    if user_session.completed:
        flash('This session is already completed.', 'info')
        return redirect(url_for('page3.confirmation'))

    # Determine which page this is based on department
    if user_session.department == 'Checkout':
        # For Checkout: this is page 4 (after YPB Daily Count and Workflow)
        current_page_number = 4
        required_page = 4
        # Check if user has access to this page (must have reached page 4)
        if user_session.max_page_reached < 4:
            flash('Please complete the Workflow page first.', 'warning')
            return redirect(url_for('page2.workflow'))
    else:
        # For other departments: this is page 3
        current_page_number = 3
        required_page = 3
        # Check if user has access to this page (must have reached page 3)
        if user_session.max_page_reached < 3:
            flash('Please complete the Workflow page first.', 'warning')
            return redirect(url_for('page2.workflow'))
    
    form = NotesForm()
    
    if request.method == 'GET':
        # Pre-populate form with existing data if available
        if user_session.notes:
            form.notes.data = user_session.notes
    
    if form.validate_on_submit():
        # Save Page 3 data
        user_session.save_page3_data(db_path, form.notes.data)
        
        # Mark session as completed
        user_session.mark_completed(db_path)
        
        # Create final submission record
        submission = FormSubmission.create_from_session(db_path, user_session)
        
        flash('Your submission has been completed successfully!', 'success')
        return redirect(url_for('page3.confirmation'))

    return render_template('notes.html', form=form, session=user_session, current_page_number=current_page_number)

@page3_bp.route('/notes/back', methods=['POST'])
@login_required
def notes_back():
    """Handle back button from Notes page to Workflow page"""
    db_path = current_app.config['DATABASE_URI']

    session_id = flask_session.get('workflow_session_id')
    if session_id:
        user_session = UserSession.get_by_session_id(db_path, session_id)
        if user_session and user_session.user_id == current_user.id:
            if user_session.department == 'Checkout':
                # For Checkout: go back to page 3 (Workflow)
                user_session.update_page(db_path, 3)
            else:
                # For other departments: go back to page 2 (Workflow)
                user_session.update_page(db_path, 2)
            return redirect(url_for('page2.workflow'))

    flash('Session error. Please log in again.', 'error')
    return redirect(url_for('auth.login'))

@page3_bp.route('/confirmation')
@login_required
def confirmation():
    """Confirmation page after successful submission"""
    db_path = current_app.config['DATABASE_URI']
    
    session_id = flask_session.get('workflow_session_id')
    if not session_id:
        flash('No active session found.', 'warning')
        return redirect(url_for('auth.login'))
    
    user_session = UserSession.get_by_session_id(db_path, session_id)
    
    if not user_session or user_session.user_id != current_user.id:
        flash('Invalid session.', 'error')
        return redirect(url_for('auth.login'))
    
    if not user_session.completed:
        flash('Please complete all pages before viewing confirmation.', 'warning')
        return redirect(url_for('page3.notes'))
    
    # Get the submission record
    submission = FormSubmission.get_all(
        db_path, 
        limit=1, 
        filters={'session_id': user_session.id}
    )
    
    submission_data = submission[0] if submission else None
    
    return render_template('confirmation.html', 
                         session=user_session, 
                         submission=submission_data)
