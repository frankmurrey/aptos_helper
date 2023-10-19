import httpx
import time

from typing import Union

from src.schemas.proxy_data import ProxyData

from loguru import logger


class ProxyManager:
    def __init__(self, proxy_data):
        self.proxy_data = proxy_data

    def get_proxy(self) -> Union[dict, None, bool]:
        proxy_data = self.proxy_data
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

    def ping(self) -> bool:
        proxies = self.get_proxy()
        if proxies is None:
            return False
        try:
            http_client = httpx.Client(proxies=proxies)
            ipify_url = 'https://api.ipify.org?format=json'
            response = http_client.get(url=ipify_url, timeout=30)

            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_ip(self) -> Union[str, None]:
        proxies = self.get_proxy()
        if proxies is None:
            return None
        try:
            http_client = httpx.Client(proxies=proxies)
            ipify_url = 'https://api.ipify.org?format=json'
            response = http_client.get(url=ipify_url, timeout=15)

            if response.status_code == 200:
                return response.json()['ip']
            else:
                return None
        except Exception as e:
            return None

    def rotate_mobile_proxy(self, rotation_link: str):
        if rotation_link is None:
            return None

        initial_ip = self.get_ip()
        if initial_ip is None:
            logger.error(f"Failed to get initial ip")
            return False

        http_client_clear = httpx.Client()
        response = http_client_clear.get(url=rotation_link)
        if response.status_code == 200:
            logger.info(f"Proxy rotation response success (current ip: {initial_ip}), "
                        f"waiting for proxy to rotate (120 sec timeout)")
            is_rotated = self.wait_for_proxy_rotation(initial_ip=initial_ip)
            if is_rotated is True:
                logger.info(f"Proxy is successfully rotated")
                return True
            else:
                logger.error(f"Proxy rotation failed or timeout")
                return False

        else:
            logger.error(f"Proxy rotation failed")
            return False

    def wait_for_proxy_rotation(self, initial_ip: str):
        start_time = time.time()
        while True:
            if time.time() - start_time > 120:
                return False

            ip = self.get_ip()
            if ip is None:
                continue

            if ip != initial_ip:
                return True

            time.sleep(2)






