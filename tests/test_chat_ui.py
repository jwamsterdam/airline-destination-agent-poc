import unittest

from fastapi.testclient import TestClient

from app.main import app


class ChatUiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_root_serves_chat_ui(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn("Destination chat", response.text)
        self.assertIn("/static/app.js", response.text)
        self.assertIn("mode-select", response.text)
        self.assertIn("language-select", response.text)
        self.assertIn("technical-panel", response.text)

    def test_static_stylesheet_is_served(self) -> None:
        response = self.client.get("/static/styles.css")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/css", response.headers["content-type"])
        self.assertIn("--brand-green", response.text)
        self.assertIn("--accent", response.text)


if __name__ == "__main__":
    unittest.main()
