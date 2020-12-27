import imghdr
from flask import current_app


def validate_img(img_file):
    """ 
        Returns the extension of an image if valid image.
        else returns None.
    """
    
    image_header = img_file.read(512)
    img_file.seek(0)
    image_type = imghdr.what(None, image_header)

    if not image_type:
        # If not image type return None.
        return None

    # Create the correct file extension and prefix with '.'
    ext_type = '.' + image_type

    # check the extension is allowed if not return None.
    if ext_type not in current_app.config['IMG_EXTENSIONS']:
        return None

    # Return image extension
    return ext_type
