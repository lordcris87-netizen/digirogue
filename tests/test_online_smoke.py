"""Real loopback smoke tests of the REST API and WebSocket matchmaking.
Run: python -m unittest discover -s tests -v
"""
import asyncio
import tempfile
import unittest
from pathlib import Path
from aiohttp.test_utils import TestClient, TestServer
import server as game


class LiveGameTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="digirogue-tests-")
        self.old_db = game.DB_PATH
        game.DB_PATH = Path(self.temp.name) / "ranking.sqlite3"
        self.server = TestServer(game.create_app())
        self.client = TestClient(self.server)
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        game.DB_PATH = self.old_db
        self.temp.cleanup()

    async def recv_type(self, sock, kind):
        async def wait():
            for _ in range(30):
                message = await sock.receive_json()
                if message.get("type") == kind:
                    return message
            raise AssertionError("Never received WebSocket message: " + kind)
        return await asyncio.wait_for(wait(), timeout=5)

    async def test_health_and_leaderboard(self):
        r = await self.client.get("/api/health")
        self.assertEqual(r.status, 200)
        health = await r.json()
        self.assertTrue(health["ok"])
        self.assertEqual(health["rooms"], 0)
        r = await self.client.get("/api/leaderboard")
        self.assertEqual(r.status, 200)
        self.assertIsInstance((await r.json())["ranking"], list)

    async def test_two_clients_create_join_and_leave(self):
        host = await self.client.ws_connect("/ws")
        guest = await self.client.ws_connect("/ws")
        try:
            hello1 = await self.recv_type(host,"hello")
            hello2 = await self.recv_type(guest,"hello")
            self.assertNotEqual(hello1["id"],hello2["id"])

            await host.send_json({"type":"create","name":"Host"})
            room = await self.recv_type(host,"joined")
            code = room["code"]
            self.assertTrue(room["host"])

            await guest.send_json({"type":"join","code":code,"name":"Guest"})
            joined = await self.recv_type(guest,"joined")
            self.assertEqual(joined["code"],code)
            self.assertFalse(joined["host"])

            await guest.send_json({"type":"input","x":1,"y":0,"attack":False})
            await host.send_json({"type":"leaderboard"})
            ranking = await self.recv_type(host,"leaderboard")
            self.assertIsInstance(ranking["rows"],list)

            health = await (await self.client.get("/api/health")).json()
            self.assertGreaterEqual(health["players"],2)

            await guest.send_json({"type":"leave"})
            await self.recv_type(guest,"left")
        finally:
            await host.close()
            await guest.close()
