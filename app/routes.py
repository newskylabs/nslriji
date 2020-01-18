
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'Peter'},
            'body': 'Hello from New York!'
        },
        {
            'author': {'username': 'Maria'},
            'body': "Let's meet in Paris!"
        },
        {
            'author': {'username': 'Nina'},
            'body': "Great trip to China!"
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
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
        return redirect(url_for('index'))

    # User is not logged in yet

    # Has the user proviced his credentials?
    form = LoginForm()
    if form.validate_on_submit():

        # Check if a user with the given credentials exists
        user = User.query.filter_by(username=form.username.data).first()

        # Authentication successfull?
        if user is None or not user.check_password(form.password.data):

            # Authentication not successfull - inform the user and ask him to try again
            flash('Invalid username or password')
            return redirect(url_for('login'))

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
        return redirect(url_for('index'))

    # No authentication data provided - show the login page 
    # and ask the user to provide his credentials
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

## fin.
