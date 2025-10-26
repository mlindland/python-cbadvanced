# tests/auth.py
import os
import unittest
from requests import Session, Request
from cbadvanced import cb_auth, client


class TestCBAuth(unittest.TestCase):
    def setUp(self):
        self.key_name = os.getenv("ADVANCED_KEY", None)
        self.key_secret = os.getenv("ADVANCED_SECRET", None)
        self.auth = cb_auth.CBAuth(self.key_name, self.key_secret)
        self.url = "https://api.coinbase.com/api/v3/brokerage/accounts"
        self.session = Session()

    def runTest(self):
        request = Request("GET", self.url).prepare()
        modified_request = self.auth(request)
        self.assertIn("Authorization", modified_request.headers)
        self.assertTrue(modified_request.headers["Authorization"].startswith("Bearer "))


class TestClientListProduct(unittest.TestCase):
    def setUp(self):
        self.key_name = os.getenv("ADVANCED_KEY", None)
        self.key_secret = os.getenv("ADVANCED_SECRET", None)
        self.client = client.Client(self.key_name, self.key_secret)

    def runTest(self):
        result = self.client.list_products()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
