import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import urlopen
from urllib.error import HTTPError

from app import HealthHandler


class HealthServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), HealthHandler)
        cls.port = cls.server.server_address[1]

        cls.thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health_returns_ok(self):
        with urlopen(
            f"http://127.0.0.1:{self.port}/health"
        ) as response:
            body = json.loads(response.read().decode())

        self.assertEqual(response.status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["service"], "health-service")
        self.assertEqual(body["version"], "1.0.0")
        self.assertIn("uptime_seconds", body)

    def test_unknown_path_returns_404(self):
        with self.assertRaises(HTTPError) as error:
            try:
                urlopen(
                    f"http://127.0.0.1:{self.port}/unknown"
                )
            except HTTPError as exc:
                exc.close()
                raise

        self.assertEqual(error.exception.code, 404)
if __name__ == "__main__":
    unittest.main()
