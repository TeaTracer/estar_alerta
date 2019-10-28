import json
import logging
import unittest
from unittest import mock
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import server

logger = logging.getLogger("test")
server.logger.setLevel(logging.DEBUG)


class MyAppTestCase(AioHTTPTestCase):
    async def get_application(self):
        return server.application(actions=False)

    @unittest_run_loop
    @mock.patch("server.healthcheck_storage")
    async def test_healthcheck_ok(self, healthcheck_storage):
        healthcheck_storage.return_value = 200
        resp = await self.client.request("GET", "/healthcheck/")
        logger.info("test_healthcheck_ok status %d", resp.status)
        assert resp.status == 200
        text = await resp.text()
        logger.info("test_healthcheck_ok text %s", text)
        assert "OK" in text

    @unittest_run_loop
    @mock.patch("server.healthcheck_storage")
    async def test_healthcheck_not_ok(self, healthcheck_storage):
        healthcheck_storage.return_value = 500
        resp = await self.client.request("GET", "/healthcheck/")
        logger.info("test_healthcheck_ok status %d", resp.status)
        assert resp.status == 200
        text = await resp.text()
        logger.info("test_healthcheck_not_ok text %s", text)
        assert "NOT OK" in text

    @unittest_run_loop
    @mock.patch("server.run_command")
    async def test_task_ok(self, run_command):
        run_command.return_value = 0
        data = json.dumps({"command": "-version"})
        resp = await self.client.request("POST", "/task/", data=data)
        assert resp.status == 200
        logger.info("test_task_ok status %d", resp.status)
        text = await resp.text()
        logger.info("test_task_ok text %s", text)
        assert "DONE" in text

    @unittest_run_loop
    @mock.patch("server.run_command")
    async def test_task_error(self, run_command):
        run_command.return_value = 1
        data = json.dumps({"command": "-version"})
        resp = await self.client.request("POST", "/task/", data=data)
        logger.info("test_task_error status %d", resp.status)
        assert resp.status == 200
        text = await resp.text()
        logger.info("test_task_error text %s", text)
        assert "ERROR" in text

    @unittest_run_loop
    @mock.patch("server.run_command")
    async def test_task_bad_json(self, run_command):
        run_command.return_value = 0
        data = "["
        resp = await self.client.request("POST", "/task/", data=data)
        logger.info("test_task_bad_json status %d", resp.status)
        assert resp.status == 400
        text = await resp.text()
        logger.info("test_task_bad_json text %s", text)
        assert "ERROR" in text
        assert "JSONDecodeError" in text

    @unittest_run_loop
    @mock.patch("server.run_command")
    async def test_task_no_command(self, run_command):
        run_command.return_value = 0
        data = json.dumps({"xxxx": "xxxx"})
        resp = await self.client.request("POST", "/task/", data=data)
        logger.info("test_task_no_command status %d", resp.status)
        assert resp.status == 400
        text = await resp.text()
        logger.info("test_task_no_command text %s", text)
        assert "ERROR" in text
        assert "ValueError" in text

    @unittest_run_loop
    @mock.patch("server.run_command")
    async def test_task_command_bad_type(self, run_command):
        run_command.return_value = 0
        data = json.dumps({"command": 1})
        resp = await self.client.request("POST", "/task/", data=data)
        logger.info("test_task_command_bad_type status %d", resp.status)
        assert resp.status == 400
        text = await resp.text()
        logger.info("test_task_command_bad_type text %s", text)
        assert "ERROR" in text
        assert "TypeError" in text


if __name__ == "__main__":
    unittest.main()
