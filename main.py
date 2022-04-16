from flask import Flask, render_template, redirect, request, make_response, jsonify, url_for
from data import db_session, books_api, users_api
from data.users import User
from data.questions import Question
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.quiz import QuizForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', title='index')


@app.errorhandler(404)
def not_found(error):
    print(error)
    return render_template("404.html", title='404')


@app.errorhandler(404)
def not_found(error):
    print(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/quiz_form/<question_number>', methods=['GET', 'POST'])
def quiz_form(question_number):
    session = db_session.create_session()
    quest = session.query(Question).filter(Question.id == question_number).first()

    form = QuizForm(quest)
    if form.validate_on_submit():
        try:
            return redirect(f'quiz_form/{question_number + 1}')
        except Exception as error:
            return redirect(f'quiz_form/result')
    return render_template('quiz.html', form=form)


@app.route('quiz_form/result')
def quiz_rezult():
    pass


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(books_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
