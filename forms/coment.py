from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ComForm(FlaskForm):
    content = TextAreaField("Комментарий")
    submit = SubmitField('Отправить')