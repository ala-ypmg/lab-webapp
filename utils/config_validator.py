"""
Configuration validation utilities to ensure secure settings
"""
import logging
import secrets
import os

logger = logging.getLogger(__name__)

# Insecure SECRET_KEY values that should never be used in production
INSECURE_SECRET_KEYS = [
    'dev',
    'test',
    'secret',
    'change',
    'your-secret-key-here',
    'dev-secret-key-change-in-production',
    'your-secret-key-here-change-in-production',
]


def validate_secret_key(secret_key, is_production=False):
    """
    Validate that SECRET_KEY is secure

    Args:
        secret_key: The SECRET_KEY value to validate
        is_production: Whether this is a production environment

    Raises:
        RuntimeError: If SECRET_KEY is insecure

    Returns:
        bool: True if valid
    """
    # Allow skipping validation for initial Vercel setup via env var
    # This should only be used temporarily while setting up environment variables
    if os.environ.get('SKIP_SECRET_KEY_VALIDATION') == 'true':
        logger.warning("SECRET_KEY validation skipped via SKIP_SECRET_KEY_VALIDATION env var")
        logger.warning("This should only be temporary - set a proper SECRET_KEY immediately!")
        return True

    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set")

    # Check if it's one of the known insecure keys
    for insecure_key in INSECURE_SECRET_KEYS:
        if insecure_key.lower() in secret_key.lower():
            error_msg = (
                f"Insecure SECRET_KEY detected (contains '{insecure_key}'). "
                f"Generate a secure key using: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
            if is_production:
                # On Vercel, log error but don't fail - allow time to set env vars
                if os.environ.get('VERCEL'):
                    logger.error(error_msg)
                    logger.error("Set proper SECRET_KEY in Vercel environment variables!")
                    logger.error("Temporarily allowing startup - FIX THIS IMMEDIATELY")
                    return True
                raise RuntimeError(error_msg)
            else:
                logger.warning(error_msg)
                return True

    # Check minimum length
    if len(secret_key) < 32:
        error_msg = "SECRET_KEY is too short (minimum 32 characters recommended)"
        if is_production:
            if os.environ.get('VERCEL'):
                logger.warning(error_msg)
            else:
                raise RuntimeError(error_msg)
        else:
            logger.warning(error_msg)

    return True


def validate_cookie_settings(app_config, is_production=False):
    """
    Validate cookie security settings

    Args:
        app_config: Flask app.config object
        is_production: Whether this is a production environment

    Raises:
        RuntimeError: If cookie settings are insecure in production

    Returns:
        bool: True if valid
    """
    issues = []

    if is_production:
        # In production, cookies must be secure
        if not app_config.get('REMEMBER_COOKIE_SECURE'):
            issues.append("REMEMBER_COOKIE_SECURE must be True in production (requires HTTPS)")

        if not app_config.get('SESSION_COOKIE_SECURE'):
            issues.append("SESSION_COOKIE_SECURE must be True in production (requires HTTPS)")

        # HTTPOnly should always be set
        if not app_config.get('SESSION_COOKIE_HTTPONLY', True):
            issues.append("SESSION_COOKIE_HTTPONLY should be True")

        if not app_config.get('REMEMBER_COOKIE_HTTPONLY', True):
            issues.append("REMEMBER_COOKIE_HTTPONLY should be True")

        # SameSite should be set
        if app_config.get('SESSION_COOKIE_SAMESITE') not in ['Lax', 'Strict']:
            issues.append("SESSION_COOKIE_SAMESITE should be 'Lax' or 'Strict'")

    if issues:
        error_msg = "Cookie security issues:\n  - " + "\n  - ".join(issues)
        if is_production:
            raise RuntimeError(error_msg)
        else:
            logger.warning(error_msg)

    return True


def validate_database_config(app_config, is_production=False):
    """
    Validate database configuration

    Args:
        app_config: Flask app.config object
        is_production: Whether this is a production environment

    Returns:
        bool: True if valid
    """
    db_uri = app_config.get('DATABASE_URI')

    if not db_uri:
        logger.error("DATABASE_URI is not configured")
        return False

    # Warn about ephemeral storage on Vercel
    if is_production and '/tmp/' in str(db_uri):
        logger.warning(
            "Using ephemeral /tmp storage for database on Vercel. "
            "Data will be lost on cold starts. Consider using a persistent database."
        )

    return True


def validate_email_config(app_config):
    """
    Validate email configuration

    Args:
        app_config: Flask app.config object

    Returns:
        bool: True if valid, False if incomplete
    """
    required_fields = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_DEFAULT_SENDER']
    missing = [field for field in required_fields if not app_config.get(field)]

    if missing:
        logger.warning(
            f"Email configuration incomplete (missing: {', '.join(missing)}). "
            f"Email features may not work."
        )
        return False

    if not app_config.get('MAIL_PASSWORD'):
        logger.warning("MAIL_PASSWORD not set. Email sending may fail.")

    return True


def validate_app_config(app):
    """
    Validate all application configuration settings

    Args:
        app: Flask application instance

    Raises:
        RuntimeError: If critical configuration errors exist in production
    """
    is_production = not app.debug and not app.testing
    env_name = "PRODUCTION" if is_production else "DEVELOPMENT"

    logger.info(f"Validating configuration for {env_name} environment")

    try:
        # Validate SECRET_KEY
        validate_secret_key(app.config.get('SECRET_KEY'), is_production)

        # Validate cookie settings
        validate_cookie_settings(app.config, is_production)

        # Validate database config
        validate_database_config(app.config, is_production)

        # Validate email config (warning only, not critical)
        validate_email_config(app.config)

        logger.info("Configuration validation completed successfully")

    except RuntimeError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def generate_secure_key():
    """
    Generate a secure random key for SECRET_KEY

    Returns:
        str: A secure random key
    """
    return secrets.token_urlsafe(32)
