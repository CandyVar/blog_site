import sqlalchemy
import datetime
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey("users.id"))
    recipient = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    message = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    sending_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=datetime.datetime.now().strftime('%#m/%d/%Y %I:%M:%S %p'))
    room_code = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f'{self.content}'
