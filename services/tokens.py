"""Token generation and confirmation for email verification"""
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_confirmation_token(email):
    """
    Generate a secure token for email confirmation
    
    Args:
        email: User's email address
        
    Returns:
        Secure token string
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')


def confirm_token(token, expiration=3600):
    """
    Confirm a token and extract the email
    
    Args:
        token: Token string to verify
        expiration: Token expiration time in seconds (default: 3600 = 1 hour)
        
    Returns:
        Email address if token is valid, False otherwise
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-confirm',
            max_age=expiration
        )
        return email
    except Exception:
        return False
