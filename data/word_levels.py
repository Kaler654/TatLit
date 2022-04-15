import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Word_level(SqlAlchemyBase):
    __tablename__ = 'word_levels'
    word_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    word_level = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now, nullable=False)
