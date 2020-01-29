
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from app.models import User, Post

@app.before_request
def before_request():
    """Remember when the user was last seen."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
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
    return render_template("index.html", title='Home Page', form=form, posts=posts)
        
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

@app.route('/user/<username>')
@login_required
def user(username):
    # Get user
    # When the username does not exist raise a 404 exception
    user = User.query.filter_by(username=username).first_or_404()

    # No error was raised - so the user exists
    # Get her posts
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    # Render user page
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

## fin.
