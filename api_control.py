import aiohttp
import asyncio

_url = ''

def setApiHost(host):
    global _url
    host = host if host.startswith('http://') else 'http://' + host
    _url = host

def prepare_url(api_path):
    result = _url
    result += api_path
    return result

setApiHost('http://127.0.0.1:8080/')

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
                raise ValueError(response.status)
            response = await response.json()
    return response

async def createUser(name, password, email, **args):
    params = {'name': name, 'password': password, 'email': email}
    for key in args.keys():
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users')
        async with session.post(url, json=params) as response:
            if response.status != 200:
                raise ValueError(response.status)
            response = await response.json()
    return response

async def deleteUser(user_id):
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/' + str(user_id))
        async with session.delete(url) as response:
            if response.status != 200:
                raise ValueError(response.status)
            response = await response.json()
    return response

async def changeUser(user_id, name, password, email, **args):
    params = {'name': name, 'password': password, 'email': email}
    for key in args.keys():
        params[key] = args[key]
    async with aiohttp.ClientSession() as session:
        url = prepare_url('api/users/' + str(user_id)) 
        async with session.put(url, json=params) as response:
            print(url)
            if response.status != 200:
                raise ValueError(response.status)
            response = await response.json()
    return response
            