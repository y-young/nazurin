from aiohttp import ClientSession, ClientTimeout, TCPConnector

from nazurin.config import PROXY, TIMEOUT, UA

class Request(ClientSession):
    """Wrapped ClientSession with default user agent, timeout and proxy support."""
    def __init__(self,
                 cookies=None,
                 headers=None,
                 timeout=ClientTimeout(total=TIMEOUT),
                 **kwargs):
        if not headers:
            headers = {}
        headers.update({'User-Agent': UA})
        connector = None
        if PROXY:
            connector = TCPConnector(verify_ssl=False)
        super().__init__(connector=connector,
                         cookies=cookies,
                         headers=headers,
                         trust_env=True,
                         timeout=timeout,
                         **kwargs)
