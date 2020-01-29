## =========================================================
## app/forms.py
## ---------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
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


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            # NOTE: 
            # When two or more processes are accessing the database at
            # the same time a race condition could cause the
            # validation to pass...
            # Very unlikely, so I'm not going to worry about it for now.
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Username already taken. Please try a different one.')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

## =========================================================
## =========================================================

## fin.
