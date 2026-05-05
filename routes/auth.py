from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from forms.login_form import LoginForm
from forms.register_form import RegistrationForm, ResendConfirmationForm
from models.user import User
from models.session import UserSession
from services.tokens import confirm_token
from services.email import send_confirmation_email, send_welcome_email
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

# Import limiter for rate limiting (will be initialized in app.py)
def get_limiter():
    """Get limiter instance from app"""
    from flask import current_app
    return current_app.extensions.get('limiter')

@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (Page 1) - handles user authentication and session creation"""
    from flask import session as flask_session

    logger.debug("Login route accessed")
    logger.debug(f"User authenticated: {current_user.is_authenticated}")

    # If user is already logged in, redirect based on their session state
    if current_user.is_authenticated:
        db_path = current_app.config['DATABASE_URI']
        active_session = UserSession.get_active_session(db_path, current_user.id)

        if active_session:
            logger.debug(f"Resuming active session for user {current_user.id}")
            # Set workflow_session_id when resuming session
            flask_session['workflow_session_id'] = active_session.session_id

            # Resume session at current page based on department
            if active_session.department == 'Accessioning':
                return redirect(url_for('accessioning.accessioning_workflow'))
            elif active_session.department == 'Checkout':
                # Checkout department workflow: Login -> YPB Daily Count -> Workflow -> Notes
                if active_session.current_page <= 2:
                    return redirect(url_for('ypb.ypb_daily_count'))
                elif active_session.current_page == 3:
                    return redirect(url_for('page2.workflow'))
                elif active_session.current_page >= 4:
                    return redirect(url_for('page3.notes'))
            else:
                # Other departments workflow: Login -> Workflow -> Notes
                if active_session.current_page <= 2:
                    return redirect(url_for('page2.workflow'))
                elif active_session.current_page >= 3:
                    return redirect(url_for('page3.notes'))
        else:
            # No active session, show login form to start new entry
            logger.debug("No active session found, logging out user")
            logout_user()
    
    form = LoginForm()
    
    if form.validate_on_submit():
        db_path = current_app.config['DATABASE_URI']
        
        # Get user from database
        user = User.get_by_user_id(db_path, form.user_id.data)
        
        if user and user.is_active and user.check_passcode(form.passcode.data):
            # Check if email is confirmed
            if not user.is_confirmed:
                flash('Please confirm your email before logging in.', 'warning')
                return redirect(url_for('auth.resend_confirmation'))
            
            # Update last login
            user.update_last_login(db_path)
            
            # Log user in
            login_user(user, remember=form.remember_me.data)
            
            # Check for existing active session
            active_session = UserSession.get_active_session(db_path, user.id)
            
            if active_session:
                # Resume existing session
                flask_session['workflow_session_id'] = active_session.session_id
                flash(f'Welcome back! Resuming your session from page {active_session.current_page}.', 'info')

                # Route based on the ACTIVE SESSION's department so that the
                # session object and the redirect destination are always in sync.
                # Using form.department.data here would cause a mismatch when the
                # user selects a different department than the one stored in the
                # session, resulting in submissions being recorded under the wrong
                # department.
                if active_session.department == 'Accessioning':
                    return redirect(url_for('accessioning.accessioning_workflow'))
                elif active_session.department == 'Checkout':
                    # Checkout department workflow: Login -> YPB Daily Count -> Workflow -> Notes
                    if active_session.current_page == 2:
                        return redirect(url_for('ypb.ypb_daily_count'))
                    elif active_session.current_page == 3:
                        return redirect(url_for('page2.workflow'))
                    elif active_session.current_page >= 4:
                        return redirect(url_for('page3.notes'))
                    else:
                        return redirect(url_for('ypb.ypb_daily_count'))
                else:
                    # Other departments workflow: Login -> Workflow -> Notes
                    if active_session.current_page >= 3:
                        return redirect(url_for('page3.notes'))
                    else:
                        return redirect(url_for('page2.workflow'))
            else:
                # Create new session with Page 1 data
                login_timestamp = datetime.now()
                new_session = UserSession.create(
                    db_path=db_path,
                    user_id=user.id,
                    login_timestamp=login_timestamp,
                    department=form.department.data,
                    remember_me=form.remember_me.data
                )
                
                # Store session_id in Flask session
                flask_session['workflow_session_id'] = new_session.session_id

                # Route based on department
                if form.department.data == 'Accessioning':
                    flash('Login successful!', 'success')
                    return redirect(url_for('accessioning.accessioning_workflow'))
                elif form.department.data == 'Checkout':
                    flash('Login successful! Please complete the YPB Daily Count.', 'success')
                    return redirect(url_for('ypb.ypb_daily_count'))
                else:
                    flash('Login successful! Please complete the workflow data.', 'success')
                    return redirect(url_for('page2.workflow'))
        else:
            flash('Invalid User ID or Passcode. Please try again.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user and clear session (POST only to prevent CSRF attacks)"""
    from flask import session as flask_session

    logger.info(f"User {current_user.id} logging out")

    # Clear workflow session
    if 'workflow_session_id' in flask_session:
        flask_session.pop('workflow_session_id')

    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


def _abandon_active_session():
    """Mark the active workflow session as completed and clear the flask session reference."""
    from flask import session as flask_session
    db_path = current_app.config['DATABASE_URI']
    session_id = flask_session.get('workflow_session_id')
    if session_id:
        user_session = UserSession.get_by_session_id(db_path, session_id)
        if user_session and user_session.user_id == current_user.id:
            user_session.mark_completed(db_path)
        flask_session.pop('workflow_session_id')


@auth_bp.route('/clear-session', methods=['POST'])
@login_required
def clear_session():
    """Abandon the current workflow session and return to login to start a fresh entry."""
    _abandon_active_session()
    flash('Session cleared. Please log in to start a new entry.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-department', methods=['POST'])
@login_required
def change_department():
    """Abandon the current workflow session and return to login to select a different department."""
    _abandon_active_session()
    flash('Session cleared. Please log in with your new department selection.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email confirmation"""
    if current_user.is_authenticated:
        return redirect(url_for('page2.workflow'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        db_path = current_app.config['DATABASE_URI']

        # Check if user_id already exists
        if User.get_by_user_id(db_path, form.user_id.data):
            # Generic message to prevent user enumeration
            flash('Registration failed. Please choose different credentials.', 'error')
            logger.warning(f"Registration attempt with existing user_id: {form.user_id.data}")
            return render_template('register.html', form=form)

        # Check if email already exists
        if User.get_by_email(db_path, form.email.data):
            # Generic message to prevent email enumeration
            flash('Registration failed. Please choose different credentials.', 'error')
            logger.warning(f"Registration attempt with existing email")
            return render_template('register.html', form=form)

        # Create new user
        user = User.create(db_path, form.user_id.data, form.email.data, form.passcode.data)

        if user:
            logger.info(f"New user registered: {form.user_id.data}")
            # Send confirmation email
            if send_confirmation_email(user.email):
                flash('Check your email to confirm your account.', 'success')
            else:
                flash('Registered, but email failed. Request a new confirmation.', 'warning')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration error. Try again.', 'error')
            logger.error(f"Failed to create user: {form.user_id.data}")
    
    return render_template('register.html', form=form)


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    """Confirm email address using token from email"""
    email = confirm_token(token)
    
    if not email:
        flash('Invalid or expired link. Request a new one.', 'error')
        return redirect(url_for('auth.resend_confirmation'))
    
    db_path = current_app.config['DATABASE_URI']
    user = User.get_by_email(db_path, email)
    
    if not user:
        flash('User not found. Please register.', 'error')
        return redirect(url_for('auth.register'))
    
    if user.is_confirmed:
        flash('Already confirmed. Please log in.', 'info')
    else:
        user.confirm_email(db_path)
        send_welcome_email(user.email, user.user_id)
        flash('Email confirmed! You can now log in.', 'success')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    """Resend confirmation email"""
    if current_user.is_authenticated:
        return redirect(url_for('page2.workflow'))
    
    form = ResendConfirmationForm()
    
    if form.validate_on_submit():
        db_path = current_app.config['DATABASE_URI']
        user = User.get_by_email(db_path, form.email.data)
        
        if user:
            if user.is_confirmed:
                flash('Already confirmed. Please log in.', 'info')
                return redirect(url_for('auth.login'))
            send_confirmation_email(user.email)
        
        # Always show same message (security)
        flash('If registered, a confirmation link will be sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('resend_confirmation.html', form=form)
