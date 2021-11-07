from aiohttp import ClientSession, TCPConnector

from nazurin.config import PROXY, UA

from .decorators import retry

class Request(ClientSession):
    get = retry(ClientSession.get)
    post = retry(ClientSession.post)
    put = retry(ClientSession.put)
    patch = retry(ClientSession.patch)
    delete = retry(ClientSession.delete)
    head = retry(ClientSession.head)
    request = retry(ClientSession.request)

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
