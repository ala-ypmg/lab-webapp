from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask import current_app


class RegistrationForm(FlaskForm):
    user_id = StringField('Display Name', validators=[
        DataRequired(message='Display name is required'),
        Length(min=2, max=50, message='Must be 2-50 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email')
    ])
    
    passcode = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Must be at least 6 characters')
    ])
    
    confirm_passcode = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('passcode', message='Passwords must match')
    ])
    
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        allowed_domain = current_app.config.get('ALLOWED_EMAIL_DOMAIN', 'ypmg.com')
        if not field.data or '@' not in field.data:
            raise ValidationError('Please enter a valid email')
        domain = field.data.lower().split('@')[-1]
        if domain != allowed_domain.lower():
            raise ValidationError(f'Registration limited to @{allowed_domain} emails only.')


class ResendConfirmationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email')
    ])
    submit = SubmitField('Resend Confirmation')
