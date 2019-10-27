import os
import logging
import asyncio
import json
import aiohttp
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
    message = b"OK\n"
    storage_status = await healthcheck_storage(request.app)
    if storage_status != 200:
        message = b"NOT OK\n"
    return web.Response(body=message)


async def on_shutdown(app):
    logger.info("on shutdown %s", app)


async def init_storage():
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
    logger.debug(command)
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


async def healthcheck_storage(app):
    minio_healthcheck_path = os.environ.get("MINIO_HEALTHCHECK_PATH")
    minio_host = os.environ.get("MINIO_HOST")
    minio_port = int(os.environ.get("MINIO_PORT"))
    url = f"http://{minio_host}:{minio_port}{minio_healthcheck_path}"

    logger.debug("start healthcheck")
    async with aiohttp.ClientSession(loop=app.loop) as session:
        logger.debug("start storage healthcheck %s", url)

        try:
            async with session.get(url, raise_for_status=False) as response:
                status = response.status
        except aiohttp.ClientError as error:
            logger.debug("storage healthcheck error %s", error)
            status = 500

        logging.debug("storage healthcheck status %d", status)
        if status != 200:
            logging.error("storage disconnected")
        return status


async def start_background_tasks(app):
    logger.debug("start init_storage")
    app["init_storage"] = asyncio.get_event_loop().create_task(init_storage())


async def cleanup_background_tasks(app):
    logger.debug("cleanup init_storage")
    app["init_storage"].cancel()
    await app["init_storage"]


def main(host, port):
    app = web.Application()

    app.router.add_route("GET", "/healthcheck/", healthcheck)
    app.router.add_route("POST", "/task/", task)

    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    app.on_shutdown.append(on_shutdown)
    logger.info("up at %s:%d", host, port)
    web.run_app(app, host=host, port=port, print=None)
    logger.info("down")
