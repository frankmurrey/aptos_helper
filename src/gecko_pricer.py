from typing import Union

from loguru import logger
from aptos_sdk.client import RestClient


class GeckoPricer:
    def __init__(self, client: RestClient):
        self.client = client

    def get_simple_price_of_token_pair(
            self,
            x_token_id: str,
            y_token_id: str
    ) -> Union[dict, None]:
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": f"{x_token_id},{y_token_id}",
                "vs_currencies": "usd"
            }

            response = self.client.client.get(
                url=url,
                params=params,
                timeout=30
            )
            if response.status_code != 200:
                return None

            data = response.json()
            x_token_price = data.get(x_token_id.lower()).get("usd")
            y_token_price = data.get(y_token_id.lower()).get("usd")

            if x_token_price is None or y_token_price is None:
                return None

            return {
                x_token_id: x_token_price,
                y_token_id: y_token_price}

        except Exception as e:
            logger.error(e)
            return None

    def is_target_price_valid(
            self,
            x_token_id: str,
            y_token_id: str,
            x_amount: Union[int, float],
            y_amount: Union[int, float],
            max_price_difference_percent: Union[int, float]) -> tuple[bool, Union[dict]]:

        try:
            gecko_coins_data: dict = self.get_simple_price_of_token_pair(
                x_token_id=x_token_id,
                y_token_id=y_token_id
            )
            if gecko_coins_data is None:
                logger.error(f"Error while getting price data from CoinGecko")
                return False, {'gecko_price': None,
                               'target_price': None}

            target_price = y_amount / x_amount
            gecko_price = gecko_coins_data[x_token_id] / gecko_coins_data[y_token_id]

            price_data = {'gecko_price': gecko_price,
                          'target_price': target_price}

            if gecko_price < target_price:
                return True, price_data

            if gecko_price > target_price:
                price_difference = gecko_price - target_price
                price_difference_percent = (price_difference / target_price) * 100
                if price_difference_percent <= max_price_difference_percent:
                    return True, price_data
                else:
                    return False, price_data

            return False, price_data

        except Exception as e:
            logger.error(f"Error while validating target price: {e}")
            return False, {'gecko_price': None,
                           'target_price': None}
