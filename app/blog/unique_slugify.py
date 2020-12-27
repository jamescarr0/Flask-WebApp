from slugify import slugify
from app.models import Post


def unique_slugify(string):
    """ 
    Query database for an existing slug and returns a unique slug 
    Will append '-number' to a slug that is not unique and increment
    further slugs with the same name. eg. slug, slug-1, slug-2
    """
    slug = slugify(string)
    unique_slug = Post.query.filter_by(slug=slug).first()

    if unique_slug is None:
        return slug

    num = 1
    new_slug = ''
    while unique_slug is not None:
        new_slug = slug + f'-{num}'
        unique_slug = Post.query.filter_by(slug=new_slug).first()
        num += 1
    return slugify(new_slug)
