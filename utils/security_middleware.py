"""
Security middleware for Flask application
Includes rate limiting and security headers
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import logging

logger = logging.getLogger(__name__)


def setup_rate_limiting(app):
    """
    Configure rate limiting for the application

    Args:
        app: Flask application instance

    Returns:
        Limiter instance
    """
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",  # Use in-memory storage (for production, consider Redis)
        strategy="fixed-window"
    )

    logger.info("Rate limiting configured")
    return limiter


def setup_security_headers(app):
    """
    Configure security headers using Flask-Talisman

    Args:
        app: Flask application instance

    Returns:
        Talisman instance
    """
    # Only enforce HTTPS in production
    force_https = not app.debug

    # Content Security Policy
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'"],  # Inline scripts for form validation
        'style-src': ["'self'", "'unsafe-inline'"],   # Inline styles
        'img-src': ["'self'", 'data:'],
        'font-src': ["'self'"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],  # Prevent clickjacking
    }

    talisman = Talisman(
        app,
        force_https=force_https,
        strict_transport_security=force_https,  # HSTS only in production
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy=csp,
        content_security_policy_nonce_in=['script-src'],
        referrer_policy='strict-origin-when-cross-origin',
        feature_policy={
            'geolocation': "'none'",
            'camera': "'none'",
            'microphone': "'none'"
        }
    )

    logger.info(f"Security headers configured (HTTPS enforcement: {force_https})")
    return talisman


def get_client_ip(request):
    """
    Get client IP address from request, considering proxies

    Args:
        request: Flask request object

    Returns:
        str: Client IP address
    """
    # Check for X-Forwarded-For header (from proxies)
    if request.headers.get('X-Forwarded-For'):
        # Take the first IP in the chain
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr

    return ip or 'unknown'
