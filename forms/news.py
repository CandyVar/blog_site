from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Скрыть с главной страницы")
    tag = StringField("Тег")
    submit = SubmitField('Применить')
    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="news")