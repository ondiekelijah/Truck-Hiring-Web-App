from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DateField,
    TextAreaField,
    SelectField
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired, Length, EqualTo, Email, Regexp
import email_validator
import flask_login
from flask_login import current_user
from wtforms import ValidationError
from wtforms import validators


class AddTruck(FlaskForm):
    truck_img = FileField(validators=[FileAllowed(["jpg", "png", "jpeg", "svg","webp"])])
    size = SelectField("Size", choices=[('Pickups'),('Canter'),('Medium'),('Treller')])
    regno = StringField(validators=[InputRequired(), Length(1, 64)])


class HireTruck(FlaskForm):
    id_no = StringField(validators=[InputRequired(), Length(8, 8)])
    phone_no = StringField(validators=[InputRequired(), Length(10,10)])
    name = StringField(validators=[InputRequired(), Length(1, 100)])
    duration = StringField(validators=[InputRequired(), Length(1, 64)])





