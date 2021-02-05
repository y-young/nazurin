import asyncio
import os

from aiohttp import ClientSession, TCPConnector

from nazurin.config import PROXY, UA

from .decorators import retry

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Request(ClientSession):
    get = retry(ClientSession.get)
    post = retry(ClientSession.post)
    head = retry(ClientSession.head)

    def __init__(self, cookies=None, headers=None, **kwargs):
        if not headers:
            headers = dict()
        headers.update({'User-Agent': UA})
        connector = None
        if PROXY:
            connector = TCPConnector(verify_ssl=False)
        super().__init__(connector=connector,
                         cookies=cookies,
                         headers=headers,
                         trust_env=True,
                         **kwargs)
