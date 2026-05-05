from flask import Blueprint

# Page 1 is handled by auth.py (login route)
# This file exists for consistency with app structure
page1_bp = Blueprint('page1', __name__)

# No additional routes needed - login is in auth.py
