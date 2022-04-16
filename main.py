from flask import Flask, render_template, redirect, request, make_response, jsonify
import datetime
from random import shuffle, choice
from data import db_session, books_api, users_api, words_api, levels_api, word_levels_api
from data.users import User
from data.questions import Question
from data import db_session, books_api, users_api, words_api, levels_api, word_levels_api
from data.users import User
from data.words import Word
from data.word_levels import Word_level
from data.levels import Level
from data.questions import Question
from data.books import Book
from forms.login import LoginForm
from forms.register import RegisterForm
from forms.add_text import TextForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from forms.quiz import QuizForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user, mixins
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from html_from_epub import convert
from bs4 import BeautifulSoup
import os
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
user_progress = {}
max_question_id = 1
quiz_analyze_session = None
table_stage2time = {
    0: 0,
    1: 1,
    2: 3,
    4: 6,
    5: 13,
    6: 28,
    7: 58,
    8: 118
}


def training_dict():
    now_time = datetime.datetime.now()
    final_dict = []
    wordlist = list(quiz_analyze_session.query(Word).all())
    userwordlist = list(quiz_analyze_session.query(Word).filter(Word.id.in_([int(i)
                                                                             for i in current_user.words.split(',')])).all())
    shuffle(wordlist)
    shuffle(userwordlist)
    for word in range(len(userwordlist)):
        word_level = quiz_analyze_session.query(Word_level).filter(Word_level.word_id == userwordlist[word].id,
                                                                   Word_level.user_id == current_user.id).first()
        date = word_level.date
        stage = word_level.word_level
        if stage == 8:
            quiz_analyze_session.delete(userwordlist[word], word_level)
            quiz_analyze_session.commit()
        last_time = datetime.datetime.fromisoformat(str(date))  # ДД-ММ-ГГ
        limit_timedelta = datetime.timedelta(days=table_stage2time[stage])
        word_level.word_level += 1
        quiz_analyze_session.commit()
        if (now_time - last_time) > limit_timedelta:
            final_dict.append([userwordlist[word].word])
            final_dict[word].append(userwordlist[word].word_ru)
            final_dict[word].append([userwordlist[word].word_ru])
            while len(final_dict[word][2]) < 4:
                ch = choice(wordlist)
                try_list = [i[0] for i in final_dict[word][2]]
                if ch.word not in try_list:
                    final_dict[word][2].append(ch.word_ru)
            shuffle(final_dict[word][2])
            for i in range(len(final_dict[word][2])):
                ind = 1 if final_dict[word][2][i] == final_dict[word][1] else 0
                final_dict[word][2][i] = (final_dict[word][2][i], ind)
    return final_dict


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ['epub']


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


@app.errorhandler(401)

@app.errorhandler(404)
def not_found(error):
    return redirect('/register')


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


@app.route('/training/<int:num>', methods=['GET', 'POST'])
@login_required
def training(num):

    return render_template('training.html', title=f'тренировка {num}')


@app.route('/books_and_texts', methods=['GET', 'POST'])
@login_required
def books_and_texts():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        return
    books = db_sess.query(Book).all()
    return render_template('books_and_texts.html', title='книги и тексты', books=books)


@app.route('/words', methods=['GET', 'POST'])
@login_required
def words():

    return render_template('words.html', title='мои слова')


@app.route('/add_text', methods=['GET', 'POST'])
@login_required
def add_text():
    form = TextForm()
    if form.validate_on_submit():
        if form.author.data and form.title.data and form.file.data and form.difficult.data:
            db_sess = db_session.create_session()
            max_id = db_sess.query(Book).order_by(Book.id).all()
            if not max_id:
                max_id = 1
            else:
                max_id = max_id[-1].id + 1
            book = Book()
            book.author = form.author.data
            book.title = form.title.data
            book.level_id = form.difficult.data
            if allowed_file(form.file.data.filename):
                f = request.files['file']
                path = f"books\{max_id}.epub"
                f.save(path)
            book.pages = 1
            book.user_author_id = current_user.id
            db_sess.merge(current_user)
            db_sess.add(book)
            db_sess.commit()
            return redirect("/books_and_texts")
        return render_template('add_text.html',
                               message="не все поля заполнены",
                               form=form)
    return render_template('add_text.html', title='добавление текста', form=form)
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
        'title': 'Quiz Result'
    }
    if user_progress[current_user.id]["showed"]:
        return render_template('quiz_rezult.html', **params)
    level_name = count / level_name
    if level_name < 0.3334:
        level_name = "Новичок"
    elif level_name < 0.6667:
        level_name = "Средний"
    else:
        level_name = "Профи"
    params["level_name"] = level_name
    user = quiz_analyze_session.query(User).filter(User.id == current_user.id).first()
    id_ = quiz_analyze_session.query(Level).filter(Level.name == level_name).first().level_id
    user.level_id = id_
    quiz_analyze_session.commit()
    user_progress[current_user.id]["showed"] = True
    return render_template('quiz_rezult.html', **params)


@app.route('/training_form', methods=['GET', 'POST'])
def training_form():
    if request.method == 'GET' and not isinstance(current_user, mixins.AnonymousUserMixin):
        try:
            if user_progress[current_user.id]["question_training_number"] == user_progress[current_user.id]['train_len']:
                user_progress[current_user.id] = {'id': current_user.id, 'question_training_number': 0,
                                                  'count_training': 0, 'showed': False,
                                                  'training_program': training_dict()}
                user_progress[current_user.id]['train_len'] = len(user_progress[current_user.id]['training_program'])
        except:
            user_progress[current_user.id] = {'id': current_user.id, 'question_training_number': 0,
                                              'count_training': 0, 'showed': False, 'training_program': training_dict()}
            user_progress[current_user.id]['train_len'] = len(user_progress[current_user.id]['training_program'])
        num = user_progress[current_user.id]['question_training_number']
        train = user_progress[current_user.id]['training_program']
        params = {
            'question': train[num][0],
            'answers': train[num][2],
            'current_answer': train[num][1],
            'title': 'Training' + train[num][0]
        }
        return render_template('quiz.html', **params)
    elif request.method == 'POST' and type(current_user) != "AnonymousUserMixin":
        if request.form is not None:
            if len(request.form) > 1:
                user_progress[current_user.id]["question_training_number"] += 1
                user_progress[current_user.id]["count_training"] += int(request.form["options"])
        if user_progress[current_user.id]['question_training_number'] == user_progress[current_user.id]['train_len']:
            return redirect('/training_result')
        return redirect('/training_form')
    else:
        return redirect('/register')


@app.route('/training_result')
def training_result():
    try:
        count = user_progress[current_user.id]["count_training"]
        level = user_progress[current_user.id]["question_training_number"]
    except:
        return redirect('/training_form')
    params = {
        'count': count,
        'level': level,
        'title': 'Training Result'
    }
    if user_progress[current_user.id]["showed"]:
        return render_template('training_rezult.html', **params)
    level_name = count / level
    if level_name < 0.3334:
        level_name = "Новичок"
    elif level_name < 0.6667:
        level_name = "Средний"
    else:
        level_name = "Профи"
    params["level_name"] = level_name
    user = quiz_analyze_session.query(User).filter(User.id == current_user.id).first()
    id_ = quiz_analyze_session.query(Level).filter(Level.name == level_name).first().level_id
    user.level_id = id_
    quiz_analyze_session.commit()
    user_progress[current_user.id]["showed"] = True
    return render_template('training_rezult.html', **params)


def set_max_question_id():
    global max_question_id, quiz_analyze_session
    quiz_analyze_session = db_session.create_session()
    max_question_id = quiz_analyze_session.query(Question).order_by(Question.id.desc()).first().id
@app.route('/book_view/<int:book_id>/<int:page>', methods=['GET', 'POST'])
def book_view(book_id, page):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    pages = book.pages
    if book and 1 <= page <= pages:
        # print(f'books/{book_id}/{book_id}.epub')
        # convert(f'books/{book_id}/{book_id}.epub')
        # shutil.move(f"{book_id}/", f"books/{book_id}/")
        html = open(f"books/{book_id}/{book_id}/content{page - 1}.html", 'r', encoding="utf-8").read()
        soup = BeautifulSoup(html, 'html.parser')

        text = soup.get_text().split("\n")
        text = [x.split() for x in text if x]
        return render_template('book_view.html', text=text, page=page, pages=pages)
    return render_template('404.html')


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
