from .auth import auth_bp
from .page1 import page1_bp
from .page2 import page2_bp
from .page3 import page3_bp
from .admin import admin_bp
from .export import export_bp
from .reports import reports_bp
from .accessioning import accessioning_bp

__all__ = [
    'auth_bp',
    'page1_bp',
    'page2_bp',
    'page3_bp',
    'admin_bp',
    'export_bp',
    'reports_bp',
    'accessioning_bp',
]
