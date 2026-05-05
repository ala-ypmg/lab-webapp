from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import Optional, Length, ValidationError
from utils.case_number import contains_case_number


def no_case_numbers(form, field):
    if field.data and contains_case_number(field.data):
        raise ValidationError('Notes may not contain case numbers or other patient identifiers.')


class NotesForm(FlaskForm):
    """Notes form for Page 3"""

    notes = TextAreaField('Notes',
        validators=[
            Optional(),
            Length(max=5000, message='Notes must not exceed 5000 characters'),
            no_case_numbers,
        ],
        render_kw={
            'placeholder': 'Enter any additional notes or comments here...',
            'rows': 10
        }
    )
