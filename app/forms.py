from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import Length, DataRequired, Email


class EditProfileForm(FlaskForm):
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EmptyForm(FlaskForm):
    """ An empty form.  Used to make POST requests as a hidden form to protect against CSRF attacks. """
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    """ The post editor form """

    title = StringField('Post title', validators=[Length(max=200), DataRequired()])
    description = TextAreaField('Description')
    day = SelectField('Day', choices=list(range(1, 32)))
    month = SelectField('Month', choices=list(range(1, 13)))
    year = SelectField('Year', choices=list(range(2020, 2030)))
    rating = SelectField('Rating', choices=list(range(6)))
    img_file = FileField('Banner image', render_kw={'multiple': True},
                         validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                                 '.jpg .jpeg .png .gif files only.')])
    img_alt = StringField('Briefly describe your image', validators=[Length(max=200)])
    submit = SubmitField('Submit')


class ContactForm(FlaskForm):
    """ Contact Form """

    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    number = StringField('Contact number (optional)', validators=[Length(max=15)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send message')