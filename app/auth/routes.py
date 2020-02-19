
from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Cooperates with load_user() function 
    # and the UserMixin used of the User class
    # (See file models.py)
    
    # Is the user logged in already?
    # current_user (imported from flask_login) contains:
    # - the user object - when user is logged in
    #   (read from the database via load_user() implemented in models.py);
    # - a special anonymous user object - when user is NOT logged in.
    if current_user.is_authenticated:
        # Redirect to the index page if the user is logged in already
        return redirect(url_for('main.index'))

    # User is not logged in yet

    # Has the user proviced his credentials?
    form = LoginForm()
    if form.validate_on_submit():

        # Check if a user with the given credentials exists
        user = User.query.filter_by(username=form.username.data).first()

        # Authentication successfull?
        if user is None or not user.check_password(form.password.data):

            # Authentication not successfull - inform the user and ask him to try again
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))

        # Authentication successfull
        # The credentials are correct: 
        # A user with the given username and password exists.
        # Log in and remember the user:
        # When other pages are accessed the current_user variable will contain that user.
        login_user(user, remember=form.remember_me.data)

        # URL parameter 'next' provided?
        # Example: /login?next=/original/page
        # When a user has been redirected to the login page from some
        # other page the original page might have been "remembered"
        # via an URL parameter.  When this is the case redirect the
        # user to the original page:
        next_page = request.args.get('next')
        if next_page and url_parse(next_page).netloc == '':
            # next_page
            #   ensures that a next page has been provided
            # url_parse(next_page).netloc == ''
            #   protects against redirection to other domains:
            #   'netloc' contains the domain of the given URL;
            #   when it is empty the URL is relative
            #   and therefore on the current domain.
            return redirect(next_page)

        # No 'next' page provided - show user the index page
        return redirect(url_for('main.index'))

    # No authentication data provided - show the login page 
    # and ask the user to provide his credentials
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


## fin.
