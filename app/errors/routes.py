from flask import render_template
from app import db

# Blueprint
from app.errors import error


@error.app_errorhandler(404)
def not_found_error(error):
    """ Returns the rendered 404 error html page. """ 
    return render_template('404.html', title="Oops, Page not found."), 404


@error.app_errorhandler(500)
def internal_error(error):
    """ Returns the rendered 500 error html page. """

    # Reset the database session.  This ensures no failed database sessions interfere with any
    # database accesses.
    db.session.rollback()
    return render_template('500.html'), 500
