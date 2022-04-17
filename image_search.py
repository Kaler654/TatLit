from distutils.command.upload import upload
from bs4 import BeautifulSoup
import requests
import os
import sys
import time


class Const:
    SEARCHER = "http://unsplash.com/search/{}"
    TRANSLATER = "https://www.translate.ru/api/getTranslation{}"
    PROMPT = "https://www.translate.ru/%D0%BF%D0%B5%D1%80%D0%B5%D0%B2%D0%BE%D0%B4/{}-{}"
    PHOTO = 'photo'
    TAT = 'татарский'
    RUS = 'русский'
    ENG = 'английский' 
    TATAR_MODE = 1
    ENGLISH_MODE = 2


url = 'https://translate.tatar/translate_hack/'


def to_normal_words(html_str, delimitel):
    try:
        ind = html_str.index(delimitel) + len(delimitel) + 1
        final_str = html_str[ind:-len(delimitel) - 3]
        return final_str
    except Exception as error:
        return None


def translate_tat_to_rus(text):
    params = {
        'lang': 1,
        'text': text
    }
    translated_text = requests.get(url, params=params).text.split('\n')
    final_json = {}
    if translated_text[0] != text:
        final_json['word'] = text
        try:
            final_json['speech_part'] = to_normal_words(translated_text[1], 'POS')
        except Exception as error:
            final_json['speech_part'] = None
        try:
            final_json['main_translation'] = to_normal_words(translated_text[-1][:-6], 'mt')
        except Exception as error:
            final_json['main_translation'] = None
        try:
            final_json['translations'] = [to_normal_words(i, 'translation') for i in translated_text[2:-3]]
        except Exception as error:
            final_json['translations'] = [None]
        try:
            final_json['examples'] = [i.split(' – ') for i in
                                      to_normal_words(translated_text[-3], 'examples').split('.  ')]
        except Exception as error:
            final_json['examples'] = [[None, None]]
        return final_json
    else:
        return final_json


def translate_rus_to_tat(text):
    params = {
        'lang': 0,
        'text': text
    }
    translated_text = requests.get(url, params=params).text.split('\n')
    final_json = {}
    if translated_text[0] != text:
        final_json['word'] = text
        try:
            final_json['speech_part'] = to_normal_words(translated_text[1], 'POS')
        except Exception as error:
            final_json['speech_part'] = None
        try:
            final_json['main_translation'] = to_normal_words(translated_text[-1][:-6], 'mt')
        except Exception as error:
            final_json['main_translation'] = None
        try:
            final_json['translations'] = [to_normal_words(i, 'translation') for i in translated_text[2:-3]]
        except Exception as error:
            final_json['translations'] = [None]
        try:
            final_json['examples'] = [i.split(' – ') for i in to_normal_words(translated_text[-3], 'examples').split('.  ')]
        except Exception as error:
            final_json['examples'] = [[None, None]]
        return final_json
    else:
        return final_json


def translate_tat_to_eng(text):
    result = translate_tat_to_rus(text)
    text = result['main_translation'] if 'main_translation' in result else ''
    return translate_rus_to_eng(text)


def translate_eng_to_tat(text):
    text = translate_eng_to_rus(text)
    result = translate_rus_to_tat(text)
    return result['main_translation'] if 'main_translation' in result else ''


def translate_rus_to_tat2(text):
    return translator(text, mode=Const.TATAR_MODE, from_lang=Const.RUS, to_lang=Const.TAT)


def translate_tat_to_rus2(text):
    return translator(text, mode=Const.TATAR_MODE, from_lang=Const.TAT, to_lang=Const.RUS)


def translate_rus_to_eng(text):
    return translator(text, mode=Const.ENGLISH_MODE, from_lang=Const.RUS, to_lang=Const.ENG)


def translate_eng_to_rus(text):
    return translator(text, mode=Const.ENGLISH_MODE, from_lang=Const.ENG, to_lang=Const.RUS)


def translator(text, mode=Const.ENGLISH_MODE, from_lang=Const.TAT, to_lang=Const.ENG):
    if mode == Const.ENGLISH_MODE:
        URL = Const.PROMPT.format(from_lang, to_lang) + '/' + text
    elif mode == Const.TATAR_MODE:
        URL = Const.PROMPT.format(from_lang, to_lang) + '?' + 'text=' + text
    with requests.sessions.Session() as session:
        response = session.get(URL)
        if response.status_code != 200:
            raise ConnectionAbortedError()
        bs = BeautifulSoup(response.content, 'lxml')
        answer = bs.find('div', {'class': 'card-body result-body'}).find('textarea').text
    return answer


def download(link, dest='a.png', folder='images'):
    if not os.path.exists(os.path.join(os.path.curdir, "images")):
        os.mkdir(folder)
    response = requests.get(link)
    if not response.status_code == 200:
        return
    with open(os.path.join(folder, dest), 'wb') as output_f:
        output_f.write(response.content)


def search(name, dest='a.png'):
    params = {'query': Const.PHOTO, 'page': 1}
    response = requests.get(Const.SEARCHER.format(name), params=params)
    if response.status_code == 200:
        # response is a html doc
        bs = BeautifulSoup(response.content, 'lxml')
        images = bs.find('div', attrs={'class': 'Z9B2b'}).find_all('img')
        for i, image in enumerate(images):
            download_link = image.get('src')
            if download_link is None:
                continue
            download(download_link, dest=f'({i}) {dest}')
    else:
        raise ConnectionAbortedError(f"You got a status {response.status_code}")
    

def search_tatar(name, dest='a.png'):
    text = translate_tat_to_eng(name)
    search(text, dest)


def search_rus(name, dest='a.png'):
    text = translate_rus_to_eng(name)
    search(text, dest)


def search_eng(name, dest='a.png'):
    search(name, dest)


if __name__ == '__main__':
    print(translate_tat_to_eng('ничек'))
