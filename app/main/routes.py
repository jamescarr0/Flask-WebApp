from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import current_user, login_required
from app import db
from app.models import User, Post

# Forms
from app.forms import EditProfileForm, EmptyForm, ContactForm

# Blueprint
from app.main import main

from app.email import send_email


@main.before_request
def before_request():
    """ A function that fires before every request.  """
    if current_user.is_authenticated:
        # Update the users last_seen field.
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@main.route('/robots.txt', methods=['GET'])
def send_from_static():
    """ Send files directly from static dir """
    return send_from_directory(current_app.static_folder, request.path[1:])


@main.route('/')
@main.route('/index')
def index():
    """ Index endpoint. """

    # Limit the posts displayed on the index page.
    posts = Post.query.order_by(Post.timestamp.desc()).limit(4)

    return render_template('index.html', title='Homepage | index.html', posts=posts)


@main.route('/explore')
@login_required
def explore():
    """ 
    Explore endpoint.
    Explore new content or find new friends/followers
    """
    # In this example..
    # Explore all users content.  Find all posts by all users and sort by timestamp

    # Pagination - .paginate(<starting from>, <number of items per page>, <bool>)
    # <bool> True returns a 404 error when out of range, False returns empty list.
    # Page defaults to 1 if if request.args returns None.

    # Pagination returns a Pagination object with a property 'items'

    page = request.args.get('page', 1, type=int)

    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'main.explore', page=posts.prev_num) if posts.has_prev else None

    return render_template("explore.html", title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@main.route('/user/<username>')
@login_required
def user(username):
    # If username does not exist trigger 404 error.

    # Get current user.
    usr = User.query.filter_by(username=username).first_or_404()

    # Set page number, return 1 as a default.
    page = request.args.get('page', 1, type=int)

    # Get all posts by current user.
    posts = usr.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)

    # Create next and previous url
    next_url = url_for('main.user', username=usr.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=usr.username,
                       page=posts.prev_num) if posts.has_prev else None

    # Create an EmptyForm - protects against CSRF.
    form = EmptyForm()

    return render_template('dashboard.html', user=usr, posts=posts.items, form=form,
                           next_url=next_url, prev_url=prev_url)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """ Edit users profile endpoint. """

    # Create the edit profile form.
    form = EditProfileForm()

    # POST Request
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile', form=form)


@main.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """ Add user to your friends/follow list """

    form = EmptyForm()

    if form.validate_on_submit():
        usr = User.query.filter_by(username=username).first()
        if usr is None:
            flash(f'User: {username} not found. ')
            return redirect(url_for('main.index'))
        if usr == current_user:
            flash('You cannot follow yourself')
            return redirect(url_for('main.user', username=username))

        # Add the specified user to your follow/friends list.
        current_user.follow(usr)

        # Commit to db
        db.session.commit()

        flash(f'You are now following {username}')

        return redirect(url_for('main.user', username=username))

    else:
        # If CSRF token is missing or invalid, redirect.
        return redirect(url_for('main.index'))


@main.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """ Remove a user from your friends/follow list """

    form = EmptyForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(username=username).first()
        if usr is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if usr == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(usr)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    """ Contact page view """
    form = ContactForm()
    if form.validate_on_submit():
        send_email(
            subject=current_app.config['WEBSITE_FORM_SUBJECT'],
            sender=current_app.config['ADMINS'][0],
            recipients=current_app.config['CLIENT_EMAIL'],
            text_body=render_template(
                'email/contact_form.txt',
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                number=form.number.data,
                message=form.message.data),
            html_body=render_template(
                'email/contact_form.html',
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                number=form.number.data,
                message=form.message.data),
        )

        flash("Message sent - Thanks for being awesome!! 🦄")
        return redirect(url_for('main.index'))
    return render_template('contact.html', title="Contact Us", form=form)
