import os
import errno
from flask import current_app
from flask_login import current_user
from werkzeug.utils import secure_filename as sf
from .validate_img import validate_img
from app.models import PostHeroImg
from .img_compressor import compress_image


def persist_img(img_file, tinymce_upload=False, **kwargs):
    """ Converts an image to JPEG, compresses and persists file to disk. """
    form = kwargs.get('form')
    post = kwargs.get('post')

    if tinymce_upload:
        upload_sub_dir = f'/user/{current_user.id}/posts/inline'
    else:
        upload_sub_dir = f'/user/{current_user.id}/posts/{post.id}'

    if img_file.filename != '':
        img_ext = validate_img(img_file.stream)
        if img_ext is None or img_ext not in current_app.config['IMG_EXTENSIONS']:
            return None

        # Create a new filename, remove existing extension. image validation extracted extension
        # from file header, will use ext returned from validation.
        original_img_filename = os.path.splitext(img_file.filename)[0]

        # Set the img extension to .JPEG and create a secure filename.
        secure_filename = sf(f'embedded_{original_img_filename}.jpeg').lower() if tinymce_upload \
            else sf(f'{post.title}_{original_img_filename}{img_ext}').lower()

        upload_dir = current_app.config['IMG_UPLOAD_PATH'] + upload_sub_dir
        upload_path = os.path.join(upload_dir, secure_filename)

        if not os.path.exists(upload_path):
            try:
                os.makedirs(upload_dir)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise

        # Compress Image before saving.
        img_file = compress_image(img_file)

        # Save file
        img_file.save(upload_path, format='JPEG', quality=80)

        image = PostHeroImg(
            img_url="/" + os.path.relpath(upload_path, current_app.root_path),
            img_alt=form.img_alt.data if not tinymce_upload else 'TinyMce Upload - Alt text added to inline styling',
            abs_path=upload_path,
            post_dir=upload_dir,
            post=post,
            user=current_user
        )

        if tinymce_upload:
            return os.path.join(upload_sub_dir, secure_filename)
        else:
            return image
