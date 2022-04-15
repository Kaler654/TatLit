import aiohttp
import asyncio


URL = "http://localhost:8080" 


def prepare_url(path):
    dest = URL + path
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


async def createUser(name, email, **args):
    params = {'name': name, 'email': email}
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
            print(url)
            if response.status != 200:
                raise ValueError("STATUS CODE: {}".format(response.status))
            response = await response.json()
    return response
            