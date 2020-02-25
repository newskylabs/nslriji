## Database Models

from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

## =========================================================
## mixin class SearchableMixin 
## ---------------------------------------------------------

class SearchableMixin(object):
    """This mixin class acts as a "glue" layer between the SQLAlchemy and
    Elasticsearch: when attached to a model class, it provides the
    ability to automatically manage an associated full-text index.

    cls.__tablename__ is used as index name.

    The class methods 'SearchableMixin.before_commit()' and
    'SearchableMixin.after_commit()' which are responsible for
    updating the index have to be bound to the corresponding data base
    events 'before_commit' and 'after_commit' in order to be triggered
    automatically as changes are made on the SQLAlchemy database.

    """

    @classmethod
    def search(cls, expression, page, per_page):
        """Searches the index with the name cls.__tablename__ for the given
        query expression.

        Example:
        
        class Post(SearchableMixin, db.Model):
            ...snip...

        query, total = Post.search('foo bar baz', 1, 5)
        total        # -> 7
        query.all()  # -> [<Post1>, <Post2>, ..., <Postk>]

        """
        # Get the list of ids of entries with a text matching the
        # query expression sorted from more to less relevant together
        # with the total number of matches.
        ids, total = query_index(cls.__tablename__, expression, page, per_page)

        # Nothing found
        if total == 0:
            return cls.query.filter_by(id=0), 0

        # Remember the order of the matches
        # by associating the id with its index in the ordered list.
        # The result can be used similar to an SQL CASE expression:
        # [(<cond1>, <res1>), (<cond2>, <res2>), ..., (<condN>, <resN>)]
        cases = []
        for i in range(len(ids)):
            cases.append((ids[i], i))

        # Retrieve the entries corresponding to the ids
        # while preserving the order by relevance 
        # 
        # cls.query.filter(cls.id.in_(ids))
        #   Retrieve the entries corresponding to the ids
        #   (in_ implements the in operator)
        #
        # .order_by(db.case(cases, value=cls.id))
        #   Order the entries: Compare the id of the entry against the
        #   first element of the pairs in the cases list.  When they
        #   match, the second element will be returned - which
        #   corresponds to the original index of the id in the list
        #   returned by query_index(), that is the relevance of the
        #   match.  This value is used to order the elements - resulting
        #   in the same order as originally returned by query_index():
        #   The order by relevance relative to the query expression.
        # 
        # The SQL code generated is similar to the following example:
        # 
        # WHERE
        #    x_field IN ('f', 'p', 'i', 'a') ...
        # ORDER BY
        #    CASE x_field
        #       WHEN 'f' THEN 1
        #       WHEN 'p' THEN 2
        #       WHEN 'i' THEN 3
        #       WHEN 'a' THEN 4
        #       ELSE 5 --needed only is no IN clause above. eg when = 'b'
        #    END, id
        # 
        # Taken from:
        # 
        #   - sql ORDER BY multiple values in specific order?
        #     https://stackoverflow.com/questions/6332043
        # 
        entries = \
            cls.query.filter(cls.id.in_(ids))\
                     .order_by(db.case(cases, value=cls.id))
        
        # Return the ordered entries 
        # together with the total number of matches
        return entries, total

    @classmethod
    def before_commit(cls, session):
        """Remember the content of what is going to be committed.

        This is intended to be used as event handler and has to be
        bound to the 'before_commit' event of the database.

        """
        # NOTE:
        # session.new, session.dirty and session.deleted
        # are available now - but their content should be used to update the 
        # search database only when the commit has been successful.
        # After the commit, however, they are not available anymore.
        # They therefore have to be stored before the commit takes place:
        session._changes = {
            'add':    list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """Retrive the content of the commit stored by before_commit() and
        update the search indices.

        This is intended to be used as event handler and has to be
        bound to the 'after_commit' event of the database.

        """
        # NOTE:
        # The session has been successfully committed -
        # session.new, session.dirty and session.deleted
        # are therefore not available anymore.
        # Retrieve the content stored before the commit has takes place
        # to update the search database:
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)

        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)

        session._changes = None

    @classmethod
    def reindex(cls):
        """Update the search index with all data from the databank.
        """
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

# Bind updates to the Elasticsearch index to SQLAlchemy events
# Events        - https://docs.sqlalchemy.org/en/latest/core/event.html
# - Core Events - https://docs.sqlalchemy.org/en/latest/core/events.html
# - ORM Events  - https://docs.sqlalchemy.org/en/latest/orm/events.html
db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit',  SearchableMixin.after_commit)

## =========================================================

# Auxiliary table 'followers'
# to define the many-to-many relationship between 
# following users 'followers' and followed users 'followed'
# Since this auxiliary table has no data other than the foreign keys, 
# it is created without an associated model class.
# The table has to be defined befor its usage in class User.
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    """
    Uses the UserMixin which implements flask_login's login procedure.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """Get the avator for the user registered at 'Gravatar'
        (http://en.gravatar.com/).  A random 'identicon' avatar is
        generated for users that do not have an avatar registered with
        the service.

        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):

        # Reset password data
        payload = {
            'reset_password': self.id, 
            'exp':            time() + expires_in
        }

        # Generate the JWT token
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

        # Convert from byte sequence to string
        tokenstr = token.decode('utf-8')

        return tokenstr

    @staticmethod
    def verify_reset_password_token(token):

        try:
            # Extract the reset password data
            payload = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )

            # Get the password
            id = payload['reset_password']

        except:
            return

        return User.query.get(id)


@login.user_loader
def load_user(id):
    """A function to load the User required by 
    flask_login's LoginManager.
    """
    return User.query.get(int(id))


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

## fin.
