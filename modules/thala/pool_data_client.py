import requests
import time
from typing import List, Optional, Union

from loguru import logger

from modules.thala import types


class PoolDataClient:
    def __init__(self, data_url: str):
        self.pool_data: Optional[types.PoolData] = None
        self.last_updated: int = 0
        self.expiry: int = 10000
        self.retry_limit: int = 3
        self.URL: str = data_url

    def get_pool_data(self) -> Union[types.PoolData, None]:
        current_time = int(time.time() * 1000)
        if not self.pool_data or current_time - self.last_updated > self.expiry:
            for i in range(self.retry_limit):
                try:
                    response = requests.get(self.URL)
                    response.raise_for_status()

                    data: types.RawPoolData = response.json()
                    coins: List[types.Coin] = [types.Coin(**coin) for coin in data['coins']]
                    pools: List[types.Pool] = [
                        types.Pool(
                            **{k: v for k, v in pool.items() if k not in ['asset0', 'asset1', 'asset2', 'asset3']},
                            asset0=coins[pool['asset0']],
                            asset1=coins[pool['asset1']],
                            asset2=coins[pool['asset2']] if 'asset2' in pool else None,
                            asset3=coins[pool['asset3']] if 'asset3' in pool else None
                        ) for pool in data['pools']
                    ]

                    self.pool_data = types.PoolData(pools=pools, coins=coins)
                    self.last_updated = current_time

                    return self.pool_data

                except requests.HTTPError as http_err:
                    logger.error(f"HTTP error occurred: {http_err}")
                    return None

                except Exception as err:
                    logger.error(f"An error occurred: {err}")
                    return None

        return self.pool_data
