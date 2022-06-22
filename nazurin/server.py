import traceback

import aiohttp_cors
import aiojobs
from aiohttp import web

from nazurin import config

class NazurinServer(web.Application):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        cors = aiohttp_cors.setup(self)
        resource = cors.add(self.router.add_resource(f"/{config.TOKEN}/api"))
        cors.add(
            resource.add_route("POST", self.update_handler), {
                "*": aiohttp_cors.ResourceOptions(
                    allow_headers=("Content-Type", ),
                    allow_methods=["POST", "OPTIONS"])
            })
        self.on_startup.append(self.init_jobs)
        self.on_shutdown.append(self.shutdown_jobs)

    def start(self):
        web.run_app(self)

    async def do_update(self, url):
        try:
            await self.bot.update_collection([url])
            await self.bot.send_message(config.ADMIN_ID,
                                        f'Successfully collected {url}')
        # pylint: disable=broad-except
        except Exception as error:
            traceback.print_exc()
            await self.bot.send_message(
                config.ADMIN_ID, f'Error processing {url}: {str(error)}')

    async def update_handler(self, request):
        data = await request.json()
        await request.app['jobs'].spawn(self.do_update(data.get('url')))
        return web.json_response({'error': 0})

    async def init_jobs(self, app):
        app['jobs'] = await aiojobs.create_scheduler()

    async def shutdown_jobs(self, app):
        await app['jobs'].close()
