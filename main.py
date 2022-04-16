from flask import Flask, render_template, redirect, request, make_response, jsonify
from data import db_session, books_api, users_api, words_api, levels_api, word_levels_api
from data.users import User
from data.questions import Question
from data.words import Word
from data.word_levels import Word_level
from data.levels import Level
from data.questions import Question
from data.books import Book
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.quiz import QuizForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user, mixins

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_progress = {}
max_question_id = 1
quiz_analyze_session = None


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


@app.route('/quiz_form', methods=['GET', 'POST'])
def quiz_form():
    if request.method == 'GET' and not isinstance(current_user, mixins.AnonymousUserMixin):
        try:
            if user_progress[current_user.id]["question_number"] == max_question_id + 1:
                user_progress[current_user.id] = {'id': current_user.id, 'question_number': 1, 'count': 0,
                                                  'showed': False}
        except:
            user_progress[current_user.id] = {'id': current_user.id, 'question_number': 1, 'count': 0, 'showed': False}
        question_number = user_progress[current_user.id]["question_number"]
        quest = quiz_analyze_session.query(Question).filter(Question.id == question_number).first()
        answers_ = [int(i) for i in str(quest.answers).split(',')]
        answers_objects = []
        for i in quiz_analyze_session.query(Word):
            if i.id in answers_:
                answers_objects.append(i.word)
        current_answer = quiz_analyze_session.query(Word).filter(Word.id == quest.correct_answer).first().word
        form = QuizForm(quest.question, answers_objects, current_answer)
        params = {
            'question': form.question,
            'answers': form.answers_list,
            'current_answer': user_progress[current_user.id]["question_number"],
            'title': 'Quiz Answer' + str(user_progress[current_user.id]["question_number"])
        }
        return render_template('quiz.html', **params)
    elif request.method == 'POST' and type(current_user) != "AnonymousUserMixin":
        if request.form is not None:
            if len(request.form) > 1:
                user_progress[current_user.id]["question_number"] += 1
                user_progress[current_user.id]["count"] += int(request.form["options"])
        if user_progress[current_user.id]["question_number"] == max_question_id + 1:
            return redirect('/quiz_result')
        return redirect('/quiz_form')
    else:
        return redirect('/register')


@app.route('/quiz_result')
def quiz_result():
    try:
        count = user_progress[current_user.id]["count"]
        level_name = user_progress[current_user.id]["question_number"] - 1
    except:
        return redirect('/quiz_form')
    params = {
        'count': count,
        'level': level_name,
        'show_message': '',
        'title': 'Quiz Result'
    }
    if user_progress[current_user.id]["showed"]:
        params['show_message'] = "в прошлый раз"
        return render_template('quiz_rezult.html', **params)
    level_name = count / level_name
    if level_name < 0.3334:
        level_name = "Новичок"
    elif level_name < 0.6667:
        level_name = "Средний"
    else:
        level_name = "Профи"
    user = quiz_analyze_session.query(User).filter(User.id == current_user.id).first()
    id_ = quiz_analyze_session.query(Level).filter(Level.name == level_name).first().level_id
    user.level_id = id_
    quiz_analyze_session.commit()
    user_progress[current_user.id]["showed"] = True
    return render_template('quiz_rezult.html', **params)


def set_max_question_id():
    global max_question_id, quiz_analyze_session
    quiz_analyze_session = db_session.create_session()
    max_question_id = quiz_analyze_session.query(Question).order_by(Question.id.desc()).first().id


def main():
    db_session.global_init("db/database.db")
    set_max_question_id()
    app.register_blueprint(books_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(words_api.blueprint)
    app.register_blueprint(levels_api.blueprint)
    app.register_blueprint(word_levels_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
