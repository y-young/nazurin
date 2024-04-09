import asyncio
import traceback
from json import JSONDecodeError

import aiohttp_cors
from aiohttp import web
from aiojobs.aiohttp import setup as setup_jobs
from aiojobs.aiohttp import spawn

from nazurin import config
from nazurin.bot import NazurinBot
from nazurin.utils import logger
from nazurin.utils.exceptions import NazurinError
from nazurin.utils.helpers import format_error


class NazurinServer(web.Application):
    def __init__(self, bot: NazurinBot):
        super().__init__()
        self.bot = bot
        cors = aiohttp_cors.setup(self)
        resource = cors.add(self.router.add_resource(f"/{config.TOKEN}/api"))
        cors.add(
            resource.add_route("POST", self.update_handler),
            {
                "*": aiohttp_cors.ResourceOptions(
                    allow_headers=("Content-Type",),
                    allow_methods=["POST", "OPTIONS"],
                ),
            },
        )
        setup_jobs(self)
        self.request_id = 1

    def start(self):
        web.run_app(self, access_log_format=config.ACCESS_LOG_FORMAT)

    async def do_update(self, url):
        try:
            logger.info("API request: {}", url)
            await self.bot.update_collection([url])
            await self.bot.send_message(
                config.ADMIN_ID,
                f"Successfully collected {url}",
            )
        except NazurinError as error:
            await self.bot.send_message(
                config.ADMIN_ID,
                f"Error processing {url}: {error}",
            )
        # pylint: disable-next=broad-exception-caught
        except Exception as error:
            traceback.print_exc()
            if isinstance(error, asyncio.TimeoutError):
                error = "Timeout, please try again."
            await self.bot.send_message(
                config.ADMIN_ID,
                f"Error processing {url}: {format_error(error)}",
            )

    async def update_handler(self, request):
        try:
            data = await request.json()
        except JSONDecodeError:
            return web.HTTPBadRequest()
        if "url" not in data:
            return web.HTTPBadRequest()
        with logger.contextualize(request=f"request:{self.request_id}"):
            await spawn(request, self.do_update(data.get("url")))
        self.request_id += 1
        return web.json_response({"error": 0})
