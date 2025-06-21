import time
import jwt
from cryptography.hazmat.primitives import serialization
import secrets
from requests.auth import AuthBase
from urllib.parse import urlparse


class CBAuth(AuthBase):
    def __init__(self, key_name, key_secret):
        self.key_name = key_name
        self.key_secret = key_secret

    def __call__(self, request):
        request.headers.update(
            {
                "Authorization": f"Bearer {self._build_jwt(self._get_uri_from_request(request))}"
            }
        )
        return request

    def _get_uri_from_request(self, request):
        """Returns Coinbase-compatible URI (method host/path) from a requests.Request object."""
        method = request.method
        parsed_url = urlparse(request.url)
        host = parsed_url.netloc
        path = parsed_url.path
        return f"{method} {host}{path}"

    def _build_jwt(self, uri):
        private_key_bytes = self.key_secret.encode("utf-8")
        private_key = serialization.load_pem_private_key(
            private_key_bytes, password=None
        )
        jwt_payload = {
            "sub": self.key_name,
            "iss": "cdp",
            "nbf": int(time.time()),
            "exp": int(time.time()) + 120,
            "uri": uri,
        }
        jwt_token = jwt.encode(
            jwt_payload,
            private_key,
            algorithm="ES256",
            headers={"kid": self.key_name, "nonce": secrets.token_hex()},
        )
        return jwt_token
