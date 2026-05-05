from flask import Blueprint, render_template, request, jsonify, current_app, session as flask_session
from flask_login import login_required, current_user
from datetime import datetime
import json
import logging
import glob
import os

from models.session import get_connection, USE_AZURE_SQL, UserSession
from utils.case_number import contains_case_number

PH = '%s' if USE_AZURE_SQL else '?'

logger = logging.getLogger(__name__)
accessioning_bp = Blueprint('accessioning', __name__)

_cached_asset: str | None = None


def _get_accessioning_asset() -> str:
    """
    Locate the compiled accessioning JS bundle inside static/assets/.
    The filename contains a content hash, e.g. 'assets/accessioning-AbCd1234.js'.
    Result is cached after the first successful lookup.
    """
    global _cached_asset
    if _cached_asset:
        return _cached_asset

    static_dir = current_app.static_folder or ''
    pattern = os.path.join(static_dir, 'assets', 'accessioning-*.js')
    # Exclude chunk files
    matches = [
        f for f in glob.glob(pattern)
        if 'chunk' not in os.path.basename(f)
    ]
    if matches:
        # Pick the most recently modified (in case of multiple builds)
        matches.sort(key=os.path.getmtime, reverse=True)
        _cached_asset = 'assets/' + os.path.basename(matches[0])
        logger.info('Accessioning asset resolved: %s', _cached_asset)
        return _cached_asset

    # Fallback: return a placeholder that will produce a 404 for the JS,
    # but at least the HTML page will load.
    logger.warning('Accessioning JS bundle not found in static/assets/ — run npm run build')
    return 'assets/accessioning-bundle.js'


@accessioning_bp.route('/accessioning-workflow', methods=['GET'])
@login_required
def accessioning_workflow():
    """Serve the Accessioning Workflow React app."""
    return render_template(
        'accessioning_workflow.html',
        session=flask_session,
        accessioning_asset=_get_accessioning_asset(),
    )


@accessioning_bp.route('/accessioning-workflow/submit', methods=['POST'])
@login_required
def accessioning_submit():
    """Receive and persist the completed accessioning session payload."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if contains_case_number(data.get('notes') or ''):
        return jsonify({
            'success': False,
            'error': 'Notes may not contain case numbers or other patient identifiers.',
        }), 400

    db_path = current_app.config['DATABASE_URI']

    # Separate connection failures from execution failures so the frontend
    # can offer a data-backup download when the database is unreachable.
    try:
        conn = get_connection(db_path)
    except Exception as exc:
        logger.error('DB connection failed during accessioning submission: %s', exc)
        return jsonify({
            'success': False,
            'error_type': 'db_unavailable',
            'error': (
                'The database is currently unavailable and your report could not be saved. '
                'Please download a backup of your session data and resubmit when the '
                'connection is restored.'
            ),
        }), 503

    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                f'''INSERT INTO accessioning_submissions
                       (user_id, submitted_at, submission_data)
                   VALUES ({PH}, {PH}, {PH})''',
                (current_user.id, datetime.now(), json.dumps(data))
            )
            conn.commit()
            logger.info(
                'Accessioning submission saved: user=%s rows=%s',
                current_user.id,
                {k: len(v) for k, v in data.get('form_data', {}).items()},
            )
        finally:
            conn.close()
    except Exception as exc:
        logger.error('Error saving accessioning submission: %s', exc)
        return jsonify({
            'success': False,
            'error': 'Your submission could not be saved. Please try again. If the problem persists, contact your administrator.',
        }), 500

    # Mark the workflow session as completed so it is not resumed on the next
    # login.  Without this, the session stays in an incomplete state and any
    # subsequent login — even with a different department — would reuse this
    # Accessioning session, causing submissions to be recorded under the wrong
    # department.
    session_id = flask_session.get('workflow_session_id')
    if session_id:
        try:
            user_session = UserSession.get_by_session_id(db_path, session_id)
            if user_session and user_session.user_id == current_user.id:
                user_session.mark_completed(db_path)
        except Exception as exc:
            logger.warning('Could not mark accessioning session as completed: %s', exc)

    return jsonify({'success': True}), 200
