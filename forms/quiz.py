from flask_wtf import FlaskForm
from wtforms.fields import RadioField
from wtforms.validators import ValidationError
from random import shuffle


class CorrectAnswer(object):
    def __init__(self, answer):
        self.answer = answer

    def __call__(self, form, field):
        message = 'Incorrect answer.'
        if field.data != self.answer:
            raise ValidationError(message)


class Answers:
    def __init__(self, answer, correct_answer):
        self.answer = answer
        self.correct_answer = correct_answer


class QuizForm(FlaskForm):
    def __init__(self, question, answers, correct_answer):
        FlaskForm.__init__(self)
        answers_list = [(i, 'False') for i in answers if i != correct_answer]
        answers_list.append((correct_answer, 'True'))
        shuffle(answers_list)
        self.q1 = RadioField(
            question,
            choices=answers_list,
            validators=[CorrectAnswer('True')])
