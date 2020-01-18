## =========================================================
## app/forms.py
## ---------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username    = StringField('Username', validators=[DataRequired()])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit      = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username  = StringField('Username', validators=[DataRequired()])
    email     = StringField('Email', validators=[DataRequired(), Email()])
    password  = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit    = SubmitField('Register')

    # Custom validators:
    # WTForms takes methods matching the pattern
    # 'validate_<field_name>' as custom validators which are invoked
    # in addition to the stock validators. 
    # When the 'ValidationError' is thrown its error message is
    # displayed next to the respective field for the user to see.

    def validate_username(self, username):
        """Ensure that the username is not used yet."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Ensure that the email is not used yet."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

## =========================================================
## =========================================================

## fin.
