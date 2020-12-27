from app import create_app, db
from datetime import datetime
from app.models import User, Post


app = create_app()


@app.context_processor
def insert_year():
    return {'current_year': datetime.utcnow().year}


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
