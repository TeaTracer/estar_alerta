import os
import logging
import asyncio
import json
from aiohttp import web

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s\t%(levelname)s\t%(message)s"
)
logger = logging.getLogger("encoder")


class NoStorageError(Exception):
    """ no connection to storage """

    pass


async def healthcheck(request):
    logger.info("healthcheck %s", request)
    status = b"OK\n"
    return web.Response(body=status)


async def on_shutdown(app):
    logger.info("on shutdown %s", app)


async def on_startup(app):
    logger.info("on startup %s", app)
    minio_host = os.environ.get("MINIO_HOST")
    minio_port = int(os.environ.get("MINIO_PORT"))
    minio_access_key = os.environ.get("MINIO_ACCESS_KEY")
    minio_secret_key = os.environ.get("MINIO_SECRET_KEY")
    minio_init_delay = int(os.environ.get("MINIO_INIT_DELAY"))
    minio_init_tries = int(os.environ.get("MINIO_INIT_TRIES"))
    command = (
        "mc config host add minio "
        f"http://{minio_host}:{minio_port} "
        f"{minio_access_key} {minio_secret_key}"
    )

    for i in range(minio_init_tries):
        logger.info("minio init %d %s", i + 1, command)
        rc = await run_command(command)
        if rc == 0:
            return
        await asyncio.sleep(minio_init_delay)
    raise NoStorageError()


async def task(request):
    logger.info("task %s", request)
    try:
        data = await request.json()
        command = data["command"]
        if not isinstance(command, str):
            raise TypeError(
                "task command should be str" ", not {}".format(type(command))
            )
    except (TypeError, json.JSONDecodeError) as error:
        logger.error(error)
        return web.Response(
            body=b"ERROR: " + repr(error).encode("utf-8") + b"\n", status=400
        )

    await run_encoder(command)

    return web.Response(body=b"DONE\n")


async def run_encoder(command):
    await run_command("ffmpeg " + command)


async def run_command(command):
    logger.info(command)
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    logger.info(f"[{command!r} exited with {proc.returncode}]")
    if stdout:
        logger.info(f"[stdout]\n{stdout.decode()}")
    if stderr:
        logger.info(f"[stderr]\n{stderr.decode()}")

    return proc.returncode


def main(host, port):
    app = web.Application()

    app.router.add_route("GET", "/healthcheck/", healthcheck)
    app.router.add_route("POST", "/task/", task)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    logger.info("up at %s:%d", host, port)
    web.run_app(app, host=host, port=port, print=None)
    logger.info("down")
