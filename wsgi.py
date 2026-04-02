"""
WSGI configuration for PythonAnywhere deployment
Update the project_home path to match your PythonAnywhere username/directory
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# UPDATE THIS PATH to match your PythonAnywhere directory
# Example: '/home/YOUR_USERNAME/lab-webapp'
project_home = '/home/YOUR_USERNAME/lab-webapp'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables from .env file
load_dotenv(Path(project_home) / '.env')

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import app as application
