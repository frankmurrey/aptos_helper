import httpx

from typing import Union

from src.schemas.wallet_data import ProxyData

from loguru import logger


class ProxyManager:

    def get_proxy(self, proxy_data: ProxyData) -> Union[dict, None, bool]:
        if proxy_data is None:
            return None

        if proxy_data.auth is False:
            return {
                "http://": f"http://{proxy_data.host}:{proxy_data.port}",
                "https://": f"http://{proxy_data.host}:{proxy_data.port}"
            }

        if proxy_data.auth is True:
            return {
                "http://": f"http://{proxy_data.username}:{proxy_data.password}@{proxy_data.host}:{proxy_data.port}",
                "https://": f"http://{proxy_data.username}:{proxy_data.password}@{proxy_data.host}:{proxy_data.port}"
            }

    def ping(self, proxy: dict) -> bool:
        print(proxy)
        http_client = httpx.Client(proxies=proxy)
        ipify_url = 'https://api.ipify.org?format=json'
        try:
            response = http_client.get(url=ipify_url, timeout=5)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

