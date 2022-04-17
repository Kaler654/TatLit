import aiohttp
import asyncio
import datetime


def prepare_url(path):
    dest = "http://localhost:8080/" + path
    if dest.count('//') > 1:
        raise("Invalid URL")
    dest = dest[:-1] if dest.endswith('/') else dest
    return dest


async def getUsers():
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/')
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(response.status)
            response = await response.json()
    return response


async def getUser(user_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/' + str(user_id))
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def createUser(name, email, password, **args):
    params = {'name': name, 'email': email, 'password': password}
    for key in args.keys():
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users')
        async with session.post(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def deleteUser(user_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/' + str(user_id))
        async with session.delete(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def changeUser(user_id, name, email, **args):
    params = {'name': name, 'email': email}
    for key in args.keys():
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/' + str(user_id)) 
        async with session.put(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def getUserWords(user_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/words/' + str(user_id))
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def getWords():
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/words/')
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def createWord(word, translation):
    params = {'word': word, 'word_ru': translation}
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/words/') 
        async with session.post(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def deleteWord(word_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/words/' + str(word_id)) 
        async with session.delete(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def changeWord(word_id, word, translation, **args):
    params = {'word': word, 'word_ru': translation}
    for key in args:
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/words/' + str(word_id))
        async with session.put(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def changeWordLevel(user_id, word_id, word_level, **args):
    params = {'user_id': user_id, 'word_id': word_id, 'word_level': word_level}
    for key in args:
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/word_levels/' + str(user_id) + '/' + str(word_id))
        async with session.put(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def getWordLevels():
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/word_levels/')
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def getWordLevel(word_level_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/word_levels/' + str(word_level_id))
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def createWordLevel(user_id, word_id, word_level, date=None):
    params = {'user_id': user_id, 'word_id': word_id, 'word_level': word_level, 'date': date}
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/word_levels')
        async with session.post(url, json=params) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def deleteWordLevel(word_level_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/word_levels/' + str(word_level_id))
        async with session.delete(url) as response:
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response


async def getWordLevel2(user_id, word_id):
    response = getWordLevels()
    for key in response.keys():
        way = response[key]
        if way['word_id'] == word_id and way['user_id'] == user_id:
            return {key: way}
    return {'error': 'Not found'}


async def getUser2(telegram_id):
    response = getUsers()
    for key in response.key():
        way = response[key]
        if way['telegram_id'] == telegram_id:
            return {key: way}
    return {'error': 'Not Found'}


async def appendWord(user_id, word_id):
    infoUser = (await getUser(user_id))[str(user_id)]
    words = infoUser['words'] + ',' + str(word_id) if infoUser['words'] is not None else str(word_id)
    await createWordLevel(user_id, word_id, 1)
    await changeUser(user_id, infoUser['name'], infoUser['email'], words=words)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete())
