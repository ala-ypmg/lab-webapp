"""Email service for sending confirmation and welcome emails"""
from flask import render_template, current_app
from flask_mail import Mail, Message
from threading import Thread

# Initialize Flask-Mail
mail = Mail()


def send_async_email(app, msg):
    """
    Send email asynchronously in background thread
    
    Args:
        app: Flask application instance
        msg: Flask-Mail Message object
    """
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")


def send_email(to, subject, template, **kwargs):
    """
    Send an email with both HTML and plain text versions
    
    Args:
        to: Recipient email address
        subject: Email subject line
        template: Template name (without extension)
        **kwargs: Template variables
    """
    app = current_app._get_current_object()
    msg = Message(
        subject=subject,
        recipients=[to],
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Render both HTML and text versions
    msg.body = render_template(f'email/{template}.txt', **kwargs)
    msg.html = render_template(f'email/{template}.html', **kwargs)
    
    # Send asynchronously
    Thread(target=send_async_email, args=(app, msg)).start()


def send_confirmation_email(user_email):
    """
    Send email confirmation link to newly registered user
    
    Args:
        user_email: User's email address
        
    Returns:
        True if email sent successfully, False otherwise
    """
    from flask import url_for
    from services.tokens import generate_confirmation_token
    
    try:
        # Generate confirmation token
        token = generate_confirmation_token(user_email)
        
        # Generate confirmation URL
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        
        # Send email
        send_email(
            to=user_email,
            subject='Confirm Your Email - YPMG Bakersfield EOS',
            template='confirm',
            confirm_url=confirm_url
        )
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False


def send_welcome_email(user_email, username):
    """
    Send welcome email after successful email confirmation
    
    Args:
        user_email: User's email address
        username: User's username
    """
    send_email(
        to=user_email,
        subject='Welcome to YPMG Bakersfield EOS',
        template='welcome',
        username=username
    )
