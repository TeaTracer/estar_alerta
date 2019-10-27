import logging
import asyncio
import json
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
    try:
        data = await request.json()
        command = data["command"]
        if not isinstance(command, str):
            raise TypeError("task command should be str, not {}".format(type(command)))
    except (TypeError, json.JSONDecodeError) as error:
        logger.error(error)
        return web.Response(body=b"ERROR: " + repr(error).encode("utf-8") + b"\n", status=400)

    await run_encoder(command)

    return web.Response(body=b"DONE\n")

async def run_encoder(command):
    cmd = "ffmpeg " + command
    logger.info(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    logger.info(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        logger.info(f'[stdout]\n{stdout.decode()}')
    if stderr:
        logger.info(f'[stderr]\n{stderr.decode()}')

def main(host, port):
    app = web.Application()

    app.router.add_route('GET', '/healthcheck/', healthcheck)
    app.router.add_route('POST', '/task/', task)

    app.on_shutdown.append(on_shutdown)
    logger.info("up at %s:%d", host, port)
    web.run_app(app, host=host, port=port, print=None)
    logger.info("down")
