import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Word_level(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'word_levels'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    word_id = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
<<<<<<< HEAD
    word_level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
=======
    word_level = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
>>>>>>> EPUB
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
