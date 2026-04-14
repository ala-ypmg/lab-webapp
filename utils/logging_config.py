"""
Centralized logging configuration for the application
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app):
    """
    Configure application-wide logging with proper handlers and formatters

    Args:
        app: Flask application instance
    """
    # Determine log level based on environment
    if app.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(detailed_formatter if app.debug else simple_formatter)
    root_logger.addHandler(console_handler)

    # File handler (only in non-Vercel environments)
    if not os.environ.get('VERCEL'):
        try:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)

            # Error file handler
            error_handler = RotatingFileHandler(
                os.path.join(log_dir, 'error.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(error_handler)
        except Exception as e:
            app.logger.warning(f"Could not create file handlers: {e}")

    # Configure Flask's app logger
    app.logger.setLevel(log_level)

    # Log startup message
    app.logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")

    return app


def get_logger(name):
    """
    Get a logger instance for a specific module

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger instance
    """
    return logging.getLogger(name)
