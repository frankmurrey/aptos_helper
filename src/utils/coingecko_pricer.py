import httpx

from loguru import logger


class GeckoPricer:
    def __init__(self, proxies=None):
        self.http_client = httpx.Client(proxies=proxies)

    def get_simple_price_of_token_pair(self,
                                       x_token_id: str,
                                       y_token_id: str):
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": f"{x_token_id},{y_token_id}",
                "vs_currencies": "usd"
            }
            response = self.http_client.get(url=url, params=params, timeout=30)
            if response.status_code != 200:
                return None

            data = response.json()

            x_token_price = data.get(x_token_id).get("usd")
            y_token_price = data.get(y_token_id).get("usd")

            if x_token_price is None or y_token_price is None:
                return None

            return {x_token_id: x_token_price,
                    y_token_id: y_token_price}

        except Exception as e:
            logger.error(e)
            return None

