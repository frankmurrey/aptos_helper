import httpx
from aptos_sdk.client import RestClient


class CustomRestClient(RestClient):
    def __init__(
            self,
            base_url: str,
            proxies: dict = None,

    ):
        super().__init__(base_url)
        self.client = httpx.Client(proxies=proxies)
