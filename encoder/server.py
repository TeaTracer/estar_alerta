import logging
import asyncio
from aiohttp import web

logging.basicConfig(level=logging.INFO, format="%(asctime)s\t%(levelname)s\t%(message)s")
logger = logging.getLogger("encoder")

async def healthcheck(request):
    logger.info("healthcheck %s", request)
    return web.Response(body=b"OK\n")

async def on_shutdown(app):
    logger.info("handle shutdown %s", app)

async def task(request):
    logger.info("task %s", request)
    await asyncio.sleep(1)
    return web.Response(body=b"DONE\n")

def main(host, port):
    app = web.Application()

    app.router.add_route('GET', '/healthcheck/', healthcheck)
    app.router.add_route('POST', '/task/', task)

    app.on_shutdown.append(on_shutdown)
    logger.info("up at %s:%d", host, port)
    web.run_app(app, host=host, port=port, print=None)
    logger.info("down")
