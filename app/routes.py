
from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Dietrich'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)
