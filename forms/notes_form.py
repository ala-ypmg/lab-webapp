from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import Optional, Length

class NotesForm(FlaskForm):
    """Notes form for Page 3"""
    
    notes = TextAreaField('Notes', 
        validators=[
            Optional(),
            Length(max=5000, message='Notes must not exceed 5000 characters')
        ],
        render_kw={
            'placeholder': 'Enter any additional notes or comments here...',
            'rows': 10
        }
    )