import traceback

import aiojobs
from aiohttp import web

from nazurin import config

class NazurinServer(web.Application):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.add_routes(
            [web.post(f'/{config.TOKEN}/api', self.update_handler)])
        self.on_startup.append(self.init_jobs)
        self.on_shutdown.append(self.shutdown_jobs)

    def start(self):
        web.run_app(self)

    async def do_update(self, url):
        try:
            await self.bot.updateCollection([url])
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
