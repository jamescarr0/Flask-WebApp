import jwt
from flask import current_app
from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
from bs4 import BeautifulSoup

from app.followers_asco_table import followers
from app.format_date import get_formatted_date
from app.custom_types import CleanedHtml


@login.user_loader
def load_user(user_id):
    """
    A function to assist tracking of logged in users.  Flask-login passes the ID of the user from the session
    and we load that user from the database.
    Flask-Login passes a string (user id), so convert id to type int before querying database.
    Retrieve and return the user from the database.
    """
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """
    User accounts class.

    Subclass UserMixin to include the generic implementations of the properties & methods flask_login requires.
        is_authenticated
        is_active
        is_anonymous
        get_id()
    """

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Creates a collection of posts linked to the User and establishes a .author attribute in the
    # Posts model using backref='name'
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    images = db.relationship('PostHeroImg', backref='user', lazy='dynamic')

    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())

    # Many - to - many followers relationship.
    # Left side is followed, right side is followers.
    # backref defines how to access the database from the right side entity (followers)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        """ The format of how to print objects of this class. """
        return f'<User id: {self.id} - {self.username}>'

    def full_name(self):
        """ Returns user full name formatted with .title() """
        return f'{self.first_name} {self.surname}'.title()

    def set_password(self, password):
        """ Hash the users password. """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """ Check password matches users password hash. """
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        """ Follow a specified user """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """ Unfollow a specified user """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """ Check is user is currently following specified user """
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """ 
        Returns All posts from the current user AND followed users filtered by timestamp in descending order.
        The first post will result in the most recent blog post.
        """
        followed_users_posts = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)

        own_posts = Post.query.filter_by(user_id=self.id)

        # Combine followed users posts and own posts into one then sort by timestamp.
        return followed_users_posts.union(own_posts).order_by(Post.timestamp.desc())

    def get_password_reset_token(self, expires_in=600):
        """
        Generates a JWT and uses .decode('utf-8') to convert to a string as JWT returns the
        token as a byte sequence by default. JWT String will be used as part of the URL.
        get token via /route/<token>
        """
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['JWT_SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_password_reset_token(token):
        """ Verifies the password reset token and returns user.id if successful. """
        try:
            # payload {reset_password : self.id }
            # Decode and use the key 'reset_password' to get the self.id value.
            # If decode fails catch error to avoid crash
            user_id = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=[
                'HS256'])['reset_password']
        except:
            # Catch JWT decode error/failure
            return

        return User.query.get(user_id)

    def get_last_seen(self):
        """ 
            Formats the last seen timestamp into a human readable
            string including an ordinal.
            eg.. 1st January, 2020    
        """
        return get_formatted_date(self.last_seen)


class Post(db.Model):
    """ A class to manage the users blog posts."""

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    slug = db.Column(db.String(125), index=True, unique=True)

    description = db.Column(CleanedHtml())
    title = db.Column(CleanedHtml())
    date_of_visit = db.Column(db.DateTime)
    rating = db.Column(db.Integer)
    view_count = db.Column(db.Integer, default=0)

    # Back reference to posts called 'author' from User model
    # backref establishes a .author attribute in this model eg (Post.author)
    # user.id references the id value from the 'users' table

    image = db.relationship('PostHeroImg', backref='post', lazy='dynamic', cascade="all, delete")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # .author - Established by the backref in User model.

    def __repr__(self):
        """ The format of how to print objects of this class. """
        return f'<Post id: {self.id} - {self.description}>'

    def snippet(self):
        """ Returns an blog post description snippet. """

        max_length = current_app.config['POST_SNIPPET_LENGTH']
        if len(self.description) < max_length:
            max_length = len(self.description)
        # Remove HTML tags for snippet, display text only.
        # Slice and add ellipsis
        return self._remove_html(self.description)[:max_length] + '...'

    def og_description(self):
        """ Returns an post snippet for OG/Facebook/Twitter/Social sharing. """

        max_length = current_app.config['POST_SNIPPET_LENGTH']
        if len(self.description) < max_length:
            max_length = len(self.description)
        return self._remove_html(self.description)[:max_length]

    def _remove_html(self, html):
        """ Removes HTML and returns text content only"""
        return BeautifulSoup(html, features="html.parser").get_text()

    def get_date_visited(self):
        """ 
            Formats the date visited timestamp into a human readable
            string including an ordinal.
            eg.. 1st January, 2020    
        """
        return get_formatted_date(self.date_of_visit)

    def get_date_created(self):
        """ 
            Formats the date created timestamp into a human readable
            string including an ordinal.
            eg.. 1st January, 2020    
        """
        return get_formatted_date(self.timestamp)


class PostHeroImg(db.Model):
    """ Hero image meta data and url address model """
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(200))
    img_alt = db.Column(db.String(200))
    abs_path = db.Column(db.String(200))
    post_dir = db.Column(db.String(200))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # post backref
    # user backref
