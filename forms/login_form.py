from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

class LoginForm(FlaskForm):
    """Login form for Page 1"""
    
    # Predefined department options
    DEPARTMENT_CHOICES = [
        ('', 'Select Department'),
        ('Accessioning', 'Accessioning'),
        ('Checkout', 'Checkout'),
        ('Histology', 'Histology'),
        ('Cytology', 'Cytology'),
        ('Grossing', 'Grossing'),
        ('Administration', 'Administration')
    ]
    
    user_id = StringField('User ID', validators=[
        DataRequired(message='User ID is required'),
        Length(min=2, max=50, message='User ID must be between 2 and 50 characters')
    ])
    
    passcode = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=4, message='Password must be at least 4 characters')
    ])
    
    department = SelectField('Department', 
        choices=DEPARTMENT_CHOICES,
        validators=[DataRequired(message='Please select a department')]
    )
    
    remember_me = BooleanField('Remember Me')
    
    def validate_department(self, field):
        """Validate that a department was selected"""
        if not field.data or field.data == '':
            raise ValidationError('Please select a department')