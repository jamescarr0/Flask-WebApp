from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """ A class to create the user login Form. """

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """ A class to create the user registration form. """

    # Email validation requires external 'email-validator' dependency.

    first_name = StringField('First name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    pin = PasswordField('Verification PIN', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # validate_<field_name>: pattern.
    # WTForms uses methods that match the validate_<field_name> as a custom validator and will invoke them
    # alongside its stock validators.

    def validate_username(self, username):
        """ Validate user input: Check username does not exist. """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            # Validation error will be displayed alongside the field that trigger the error.
            raise ValidationError(
                'Username already exists, please choose a different username.')

    def validate_email(self, email):
        """ Validate user input: Check email address does not exist. """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            # Validation error will be displayed alongside the field that trigger the error.
            raise ValidationError(
                'This email address is already associated with another account.')


class ResetPasswordRequestForm(FlaskForm):
    """ The password reset REQUEST form """
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    """ The password reset form """
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Save new password')
