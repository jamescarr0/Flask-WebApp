import os
import shutil
from app import db
from flask import current_app, render_template, abort, Response, request, redirect, url_for, flash, jsonify, make_response
from flask_login import current_user, login_required
from datetime import datetime

from app.models import Post
from app.forms import PostForm, EmptyForm
from .persist_img import persist_img
from .unique_slugify import unique_slugify

from . import blog


@blog.route('/posts', methods=['GET'])
def view_all():
    """ Returns all blog post entries """
    page = request.args.get('page', 1, type=int)

    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for(
        'blog.view_all', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'blog.view_all', page=posts.prev_num) if posts.has_prev else None

    return render_template("all_posts.html", title='Flask Project | Blog', posts=posts.items, next_url=next_url,
                           prev_url=prev_url, page_num=posts.page, page_count=posts.pages)


@blog.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    """ 
    Create_post endpoint.
    Creates the post form and saves blog entry to database. 
    """

    form = PostForm()

    # Check if this is a tinyMce image upload.
    if request.method == 'POST':
        if request.files.get('file'):
            try:
                file = persist_img(request.files.get('file'), tinymce_upload=True)
            except Exception as err:
                print("ERROR with: ", err)
                abort(404)
                # Return image path back to editor
            return jsonify({'location': file})

    # POST request
    if form.validate_on_submit():
        post = Post(
            slug=unique_slugify(form.title.data),
            title=form.title.data,
            description=form.description.data,
            date_of_visit=datetime(int(form.year.data), int(
                form.month.data), int(form.day.data)),
            rating=form.rating.data,
            author=current_user
        )
        # Flush to get post id
        db.session.add(post)
        db.session.flush()

        img_file = request.files['img_file']
        if img_file:
            image = persist_img(img_file, form=form, post=post)
            db.session.add(image)

        db.session.commit()

        flash('Your post is now live!')

        # Respond to POST request with a redirect. - Avoids browser confirming duplicate submission.
        return redirect(url_for('main.index'))

    return render_template('create_post.html', title='Create a new blog post', form=form)


@blog.route('/post/<slug>')
def post_detail(slug):
    """ Return full post entry update view count """
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    # Update the view count.  Check post has attribute.
    # If admin edits an article and slug changes whilst a user is reading the current argument
    # An AttributeError 'NoneType' will be thrown.  Check current object has the view_count attr.
    if hasattr(post, 'view_count'):
        post.view_count += 1
        db.session.add(post)
        db.session.commit()

    # Hero image object.  If no image saved return None.  Jinja will test
    # and not include the hero section when rendering.
    try:
        hero = post.image[0]
    except IndexError:
        hero = None

    return render_template('article.html', title=post.title, post=post, hero=hero)


@blog.route('/edit-post/<slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    """ Edits an existing blog entry """

    post = Post.query.filter_by(slug=slug).first()
    form = PostForm(obj=post)

    try: existing_hero = post.image[0]
    except IndexError: existing_hero = None

    if request.method == 'GET':
        # Set the select field (drop down menu) values for a get request.
        form.day.data = post.date_of_visit.strftime('%-d')
        form.month.data = post.date_of_visit.strftime('%-m')
        form.year.data = post.date_of_visit.strftime('%-Y')

    if form.validate_on_submit():
        form.populate_obj(post)

        post.date_of_visit = datetime(int(form.year.data), int(
            form.month.data), int(form.day.data))

        # Check if user has uploaded a new hero/banner image; and update.
        img_file = request.files['img_file']
        new_image = persist_img(img_file, form=form, post=post) if img_file else None
        
        if new_image:
            
            # Check if an existing image is on disk and remove/replace.
            if existing_hero:
                # Remove hero image data from database
                db.session.delete(existing_hero)
               
                # Remove file from disk
                os.remove(existing_hero.abs_path) 

            db.session.add(new_image)
        
        db.session.commit()
        return redirect(url_for('main.user', username=current_user.username))

    return render_template('create_post.html', title=post.title, form=form)


@blog.route('/delete-post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """ Deletes a post entry """

    form = EmptyForm()

    if form.validate_on_submit():
        post = Post.query.get(post_id)

        # Check the current user owns the post to prevent unauthorised deleting of users posts.
        if post.author == current_user:
            try:
                # Remove post directory and image from disk.
                shutil.rmtree(post.image[0].post_dir)
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}")
            
            db.session.delete(post)
            db.session.commit()

    return redirect(url_for('main.user', username=current_user.username))
