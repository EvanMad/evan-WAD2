from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, FloatField, ValidationError, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange, InputRequired
from .db_manager import *

from . import db
from . import models

# Forms for user Authentication, displayed in log in and sign up pages 
class LoginForm(FlaskForm):
    name = FloatField('name', validators=[DataRequired()])
    password = StringField('password', validators=[
        DataRequired()])

class SignupForm(FlaskForm):
    name = FloatField('name', validators=[DataRequired()])
    password = StringField('password', validators=[
        DataRequired()])

# Form for creating reviews, displayed in review page
# TODO: additional validation
class ReviewForm(FlaskForm):
    # rating = FloatField('rating', validators=[InputRequired(), NumberRange(min=0, max=10, message="Rating must be between 0 and 10")])
    rating = DecimalField('rating', validators=[NumberRange(min=0, max=10, message='bla')])
    content = TextAreaField('content', validators=[DataRequired()])
    rollercoaster = SelectField('rollercoaster', validators=[DataRequired()])
