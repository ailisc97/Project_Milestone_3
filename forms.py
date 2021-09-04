from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(min=4, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Repeat Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')


class CreatePlacesForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tags = StringField('Tags (separate by comma please)', validators=[DataRequired()])
    image = StringField('Image Link (full path)', validators=[DataRequired()])
    submit = SubmitField('Add Restaurant')


class EditPlacesForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    tags = StringField('Tags (separate by comma please)', validators=[DataRequired()])
    image = StringField('Image Link (full path)', validators=[DataRequired()])
    submit = SubmitField('Update Restaurant')


class ConfirmDelete(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Delete this Restaurant')
