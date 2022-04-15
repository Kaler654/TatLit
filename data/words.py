import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Word(SqlAlchemyBase):
    __tablename__ = 'words'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=False)
    word = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    word_ru = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
