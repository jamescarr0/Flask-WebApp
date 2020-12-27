from flask import request, redirect, url_for, flash, render_template, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.models import User

from . import auth
from .email import send_password_reset_email
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ Login endpoint. """

    # If user is already logged in/authenticated redirect user.
    if current_user.is_authenticated:
        return redirect(url_for('main.user', username=current_user.username))

    # Create the user login form.
    form = LoginForm()

    # Returns False on GET request.  On POST request the validators check form is valid
    # and if everything is ok, returns True, indicating the data is valid.
    if form.validate_on_submit():

        # Search for the username passed from the html login form.
        # If user does not exist or password is invalid, redirect back to login page.

        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('auth.login'))

        # User found & password correct - Login user.
        # 'Remember me' check box on login form returns true/false.
        login_user(user, remember=form.remember_me.data)

        # If user requested a page and was not logged in, get the original URL they were requesting
        # and redirect back to the original URL once logged in.
        # request.args contains this in the 'next' attribute.  Example: /login?next=/index.

        original_url_req = request.args.get('next')

        # Determine if URL is relative or absolute.  Redirects must stay within the same site as application.
        # Attacker could insert a URL to a malicious site in the 'next' argument.
        # < scheme >: // < netloc > / < path >; < params >? < query >  # <fragment>
        # http://www.domain.com/index?query=something

        if not original_url_req or url_parse(original_url_req).netloc != '':
            # if url does not have a next argument or url is absolute.  Set redirect to index.
            original_url_req = url_for('main.index')

        return redirect(original_url_req)

    # Render the login template & login form.
    return render_template('login.html', title='Sign In', form=form)


@auth.route('/logout')
def logout():
    """ Logout endpoint. """
    # Use flasks logout_user() function.
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """ Register endpoint. """

    # If user is authenticated redirect
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Create registration form.
    form = RegistrationForm()

    # POST Request
    if form.validate_on_submit():
        # Convert to lowercase, create a new user and hash the password.
        if form.pin.data != current_app.config['REGISTRATION_PIN']:
            flash('Registration PIN code required.  Please contact admin for PIN request')
            return redirect(url_for('main.index'))

        new_user = User(
            first_name=form.first_name.data.lower(),
            surname=form.surname.data.lower(),
            username=form.username.data.lower(),
            email=form.email.data.lower())
        new_user.set_password(form.password.data)

        # Add new_user and commit to database.
        db.session.add(new_user)
        db.session.commit()

        flash('User registration successful.')

        # Log new user in and redirect.
        login_user(new_user)
        return redirect(url_for('main.index'))

    return render_template('register.html', form=form)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """ Reset Password REQUEST endpoint """

    # If user is authenticated redirect.
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()

    # POST request
    if form.validate_on_submit():
        # Get user by email address
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)

        # Keep feedback message outside of if user for security
        # Stops users guessing usernames and will flash regardless if a user is found or not.
        flash('Check your email to reset your password.')

        return redirect(url_for('auth.login'))

    # GET request
    return render_template('reset_password_request.html', title='Password reset', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """ Reset and save a new password endpoint """

    if current_user.is_authenticated:
        # If authenticated / logged in, redirect
        return redirect(url_for('main.index'))

    # Verify the token.
    user = User.verify_password_reset_token(token)
    print(f'User verified as: {user}')

    if not user:
        # If no user is returned, redirect.
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()

    # POST REQUEST
    if form.validate_on_submit():
        # WTF form validators have validated matching passwords from forms.py
        # Set the new password
        user.set_password(form.password.data)
        # Commit the new password to database.
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    # GET Request
    return render_template('reset_password.html', form=form)
