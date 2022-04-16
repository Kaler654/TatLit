import sqlalchemy
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=False)
    answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    correct_answer = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
