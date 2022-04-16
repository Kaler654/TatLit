from flask import Flask, render_template, redirect, request, make_response, jsonify
from data import db_session, books_api, users_api, words_api, levels_api, word_levels_api
from data.users import User
from data.words import Word
from data.word_levels import Word_level
from data.levels import Level
from data.questions import Question
from data.books import Book
from forms.login import LoginForm
from forms.register import RegisterForm
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from html_from_epub import convert
from bs4 import BeautifulSoup
import os
import shutil

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
    app.register_blueprint(books_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.register_blueprint(words_api.blueprint)
    app.register_blueprint(levels_api.blueprint)
    app.register_blueprint(word_levels_api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()