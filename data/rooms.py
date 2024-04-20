import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'rooms'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    code = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('chats.room_code'))
    members = sqlalchemy.Column(sqlalchemy.String)
