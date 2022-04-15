from flask import Blueprint, jsonify, make_response, request
from . import db_session
from .words import Word
from .users import User

blueprint = Blueprint(
    'words_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/words/<int:user_id>', methods=["GET"])
def get_user_words(user_id):
    db_sess = db_session.create_session()
    user_words_id = db_sess.query(User.words).filter(User.id == user_id).first()
    print(user_words_id[0])
    words = db_sess.query(Word).filter(Word.id.in_(list(map(int, user_words_id[0].split(','))))).all()
    print(words)
    return jsonify(
        {item.id: item.to_dict(only=('word', 'word_ru')) for item in words}
    )


@blueprint.route('/api/words', methods=["GET"])
def get_words():
    db_sess = db_session.create_session()
    words = db_sess.query(Word).all()
    return jsonify(
        {item.id: item.to_dict(only=('word', 'word_ru')) for item in words}
    )


@blueprint.route('/api/words', methods=['POST'])
def create_word():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['word', 'word_ru']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    word = Word(
        word=request.json['word'],
        word_ru=request.json['word_ru']
    )
    db_sess.add(word)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    db_sess = db_session.create_session()
    word = db_sess.query(Word).get(word_id)
    if not word:
        return jsonify({'error': 'Not found'})
    db_sess.delete(word)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/words/<int:word_id>', methods=['PUT'])
def edit_word(word_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['word', 'word_ru']):
        return jsonify({'error': 'Bad put request'})

    db_sess = db_session.create_session()
    word = db_sess.query(Word).filter(Word.id == word_id).first()
    if word:
        word.word = request.json['word']
        word.word_ru = request.json['word_ru']
        db_sess.commit()
        return jsonify({'success': 'OK'})
    return jsonify({'error': 'EERRERERRERERERERERER'})
