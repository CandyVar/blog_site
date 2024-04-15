from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class MessageForm(FlaskForm):
    content = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('->')
