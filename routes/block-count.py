from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session as flask_session, jsonify
from flask_login import login_required, current_user
from models.session import UserSession
import glob
import logging
import json
import os

logger = logging.getLogger(__name__)
ypb_bp = Blueprint('ypb', __name__)

_cached_ypb_asset: str | None = None


def _get_ypb_asset() -> str:
    """Locate the compiled YPB Daily Count JS bundle inside static/assets/."""
    global _cached_ypb_asset
    if _cached_ypb_asset:
        return _cached_ypb_asset
    static_dir = current_app.static_folder or ''
    pattern = os.path.join(static_dir, 'assets', 'index-*.js')
    matches = [f for f in glob.glob(pattern) if 'chunk' not in os.path.basename(f)]
    if matches:
        matches.sort(key=os.path.getmtime, reverse=True)
        _cached_ypb_asset = 'assets/' + os.path.basename(matches[0])
        logger.info('YPB asset resolved: %s', _cached_ypb_asset)
        return _cached_ypb_asset
    logger.warning('YPB JS bundle not found in static/assets/ — run npm run build')
    return 'assets/index-bundle.js'

@ypb_bp.route('/ypb-daily-count', methods=['GET', 'POST'])
@login_required
def ypb_daily_count():
    """Page 2 for Checkout Department - YPB Daily Count"""
    db_path = current_app.config['DATABASE_URI']

    logger.debug("YPB Daily Count route accessed")

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

    # Only Checkout department should access this page
    if user_session.department != 'Checkout':
        flash('This page is only available for Checkout department.', 'error')
        return redirect(url_for('page2.workflow'))

    # Check if user has access to this page (must have reached at least page 2)
    if user_session.max_page_reached < 2:
        user_session.update_page(db_path, 2)

    # Handle POST request (form submission from React app)
    if request.method == 'POST':
        try:
            # Get JSON data from React app
            data = request.get_json()

            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400

            # Store YPB daily count data in session
            # For now, we'll store it as JSON in a new field
            # You may want to add specific fields to the database schema later
            ypb_data_json = json.dumps(data)

            # Save to session (we'll need to add a field for this)
            # For now, we can use the notes field temporarily or add a new field
            user_session.save_ypb_data(db_path, ypb_data_json)

            # Update to page 3 (which is now the workflow page)
            user_session.update_page(db_path, 3)

            logger.info(f"YPB Daily Count data saved for session {session_id}")

            return jsonify({'success': True, 'redirect': url_for('page2.workflow')}), 200

        except Exception as e:
            logger.error(f"Error saving YPB Daily Count data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # GET request - render the React app
    return render_template('ypb_daily_count.html', session=flask_session, user_session=user_session,
                           ypb_asset=_get_ypb_asset())

@ypb_bp.route('/ypb-daily-count/back', methods=['POST'])
@login_required
def ypb_daily_count_back():
    """Handle back button from YPB Daily Count to Page 1"""
    db_path = current_app.config['DATABASE_URI']

    session_id = flask_session.get('workflow_session_id')
    if session_id:
        user_session = UserSession.get_by_session_id(db_path, session_id)
        if user_session and user_session.user_id == current_user.id:
            # Update current page to 1
            user_session.update_page(db_path, 1)

    flash('Returning to login page.', 'info')
    return redirect(url_for('auth.logout'))
