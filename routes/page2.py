from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session as flask_session
from flask_login import login_required, current_user
from forms.workflow_form import WorkflowForm
from models.session import UserSession
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
page2_bp = Blueprint('page2', __name__)

@page2_bp.route('/workflow', methods=['GET', 'POST'])
@login_required
def workflow():
    """Page 2/3 - Workflow Data Entry (Page 2 for non-Checkout, Page 3 for Checkout)"""
    db_path = current_app.config['DATABASE_URI']

    logger.debug("Workflow route accessed")

    # Get or validate session
    session_id = flask_session.get('workflow_session_id')
    if not session_id:
        logger.warning(f"No session_id found for user {current_user.id}")
        flash('Session not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    user_session = UserSession.get_by_session_id(db_path, session_id)

    if not user_session or user_session.user_id != current_user.id:
        logger.warning(f"Invalid session access attempt by user {current_user.id}")
        flash('Invalid session. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    # Check if session is completed
    if user_session.completed:
        flash('This session is already completed. Please start a new entry.', 'info')
        return redirect(url_for('auth.logout'))

    # Determine which page this is based on department
    if user_session.department == 'Checkout':
        # For Checkout: this is page 3 (after YPB Daily Count)
        current_page_number = 3
        # Check if user has access to this page (must have reached at least page 3)
        if user_session.max_page_reached < 3:
            user_session.update_page(db_path, 3)
    else:
        # For other departments: this is page 2
        current_page_number = 2
        # Check if user has access to this page (must have reached at least page 2)
        if user_session.max_page_reached < 2:
            user_session.update_page(db_path, 2)

    # Check if department is one that shows "Coming Soon" placeholder
    coming_soon_departments = ['Cytology', 'Grossing', 'Administration']
    if user_session.department in coming_soon_departments:
        return render_template('coming_soon.html', session=user_session)
    
    form = WorkflowForm()
    
    if request.method == 'GET':
        # Pre-populate form with existing data if available
        if user_session.final_block_time:
            form.final_block_time.data = datetime.strptime(user_session.final_block_time, '%H:%M').time()
        form.baked_ihcs_pt_link.data = user_session.baked_ihcs_pt_link
        form.ihcs_in_pt_link.data = user_session.ihcs_in_pt_link
        form.non_baked_ihc.data = user_session.non_baked_ihc
        form.ihcs_in_buffer_wash.data = user_session.ihcs_in_buffer_wash
        form.pathologist_requests_status.data = user_session.pathologist_requests_status
        form.request_source_email.data = user_session.request_source_email or False
        form.request_source_orchard.data = user_session.request_source_orchard or False
        form.request_source_send_out.data = user_session.request_source_send_out or False
        form.in_progress_her2.data = user_session.in_progress_her2
        form.upfront_special_stains.data = user_session.upfront_special_stains
        form.peloris_maintenance.data = user_session.peloris_maintenance
    
    if form.validate_on_submit():
        # Prepare data dictionary
        workflow_data = {
            'final_block_time': form.final_block_time.data.strftime('%H:%M') if form.final_block_time.data else None,
            'baked_ihcs_pt_link': form.baked_ihcs_pt_link.data,
            'ihcs_in_pt_link': form.ihcs_in_pt_link.data,
            'non_baked_ihc': form.non_baked_ihc.data,
            'ihcs_in_buffer_wash': form.ihcs_in_buffer_wash.data,
            'pathologist_requests_status': form.pathologist_requests_status.data,
            'request_source_email': form.request_source_email.data,
            'request_source_orchard': form.request_source_orchard.data,
            'request_source_send_out': form.request_source_send_out.data,
            'in_progress_her2': form.in_progress_her2.data,
            'upfront_special_stains': form.upfront_special_stains.data,
            'peloris_maintenance': form.peloris_maintenance.data
        }
        
        # Save Page 2/3 data to session
        user_session.save_page2_data(db_path, workflow_data)

        # Update to next page based on department
        if user_session.department == 'Checkout':
            # For Checkout: move to page 4 (Notes)
            user_session.update_page(db_path, 4)
        else:
            # For other departments: move to page 3 (Notes)
            user_session.update_page(db_path, 3)

        flash('Workflow data saved successfully.', 'success')
        return redirect(url_for('page3.notes'))

    return render_template('workflow.html', form=form, session=user_session, current_page_number=current_page_number)

@page2_bp.route('/workflow/back', methods=['POST'])
@login_required
def workflow_back():
    """Handle back button from Workflow page"""
    db_path = current_app.config['DATABASE_URI']

    session_id = flask_session.get('workflow_session_id')
    if session_id:
        user_session = UserSession.get_by_session_id(db_path, session_id)
        if user_session and user_session.user_id == current_user.id:
            if user_session.department == 'Checkout':
                # For Checkout: go back to page 2 (YPB Daily Count)
                user_session.update_page(db_path, 2)
                flash('Returning to YPB Daily Count.', 'info')
                return redirect(url_for('ypb.ypb_daily_count'))
            else:
                # For other departments: go back to page 1 (Login)
                user_session.update_page(db_path, 1)
                flash('Returning to login page.', 'info')
                return redirect(url_for('auth.logout'))

    flash('Session error. Please log in again.', 'error')
    return redirect(url_for('auth.login'))
