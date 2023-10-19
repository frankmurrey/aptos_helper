from typing import Union

from loguru import logger

from src.schemas.proxy_data import ProxyData


def parse_proxy_data(proxy_str: str) -> Union[ProxyData, None]:
    if not proxy_str:
        return None

    try:
        if proxy_str.startswith('m$'):
            is_mobile = True
            proxy_str = proxy_str[2:]
        else:
            is_mobile = False

        proxy_str = proxy_str.split(":")
        if len(proxy_str) == 2:
            host, port = proxy_str
            proxy = ProxyData(
                host=host,
                port=port,
                is_mobile=is_mobile
            )

        elif len(proxy_str) == 4:
            host, port, username, password = proxy_str
            proxy = ProxyData(
                host=host,
                port=port,
                username=username,
                password=password,
                auth=True,
                is_mobile=is_mobile
            )

        else:
            proxy = None

        return proxy

    except Exception as e:
        logger.error(f"Error while parsing proxy data: {e}")
        logger.exception(e)
        return None
