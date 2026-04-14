"""
Vercel serverless function entry point
"""
from app import app

# Vercel expects an 'app' or 'handler' to be exported
# Flask apps work directly as WSGI applications
