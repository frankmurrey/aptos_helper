from typing import List, Optional
from enum import Enum


class Edge:
    def __init__(self, pool: 'LiquidityPool', from_index: int, to_index: int):
        self.pool = pool
        self.from_index = from_index
        self.to_index = to_index


class SwapPath:
    def __init__(self, from_coin: str, to: str, pool: 'LiquidityPool'):
        self.from_coin = from_coin
        self.to = to
        self.pool = pool


class RouteType(Enum):
    EXACT_INPUT = "exact_input"
    EXACT_OUTPUT = "exact_output"


class Route:
    def __init__(
            self,
            path: List[SwapPath],
            amount_in: int,
            amount_out: int,
            price_impact_percentage: float,
            route_type: 'RouteType'
    ):
        self.path = path
        self.amount_in = amount_in
        self.amount_out = amount_out
        self.price_impact_percentage = price_impact_percentage
        self.route_type = route_type


class PoolType(Enum):
    EXACT_INPUT = "stable_pool"
    EXACT_OUTPUT = "weighted_pool"


class LiquidityPool:
    def __init__(
            self,
            coin_addresses: List[str],
            balances: List[int],
            pool_type: 'PoolType',
            swap_fee: float,
            weights: Optional[List[int]] = None,
            amp: Optional[int] = None

    ):
        self.coin_addresses = coin_addresses
        self.balances = balances
        self.pool_type = pool_type
        self.swap_fee = swap_fee
        self.weights = weights
        self.amp = amp


class Coin:
    def __init__(self, address: str, decimals: int):
        self.address = address
        self.decimals = decimals


class PoolBase:
    def __init__(self,
                 name: str,
                 balance0: int,
                 balance1: int,
                 balance2: Optional[int] = None,
                 balance3: Optional[int] = None,
                 amp: Optional[int] = None
                 ):
        self.name = name
        self.balance0 = balance0
        self.balance1 = balance1
        self.balance2 = balance2
        self.balance3 = balance3
        self.amp = amp


class RawPool(PoolBase):
    def __init__(self, asset0: int, asset1: int, asset2: Optional[int] = None, asset3: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.asset0 = asset0
        self.asset1 = asset1
        self.asset2 = asset2
        self.asset3 = asset3


class Pool(PoolBase):
    def __init__(self,
                 name: str,
                 balance0: float,
                 balance1: float,
                 asset0: Coin,
                 asset1: Coin,
                 asset2: Optional[Coin] = None,
                 asset3: Optional[Coin] = None,
                 balance2: Optional[float] = None,
                 balance3: Optional[float] = None,
                 amp: Optional[float] = None):
        super().__init__(name, balance0, balance1, balance2, balance3, amp)
        self.asset0 = asset0
        self.asset1 = asset1
        self.asset2 = asset2
        self.asset3 = asset3


class RawPoolData:
    def __init__(self, pools: List[RawPool], coins: List[Coin]):
        self.pools = pools
        self.coins = coins


class PoolData:
    def __init__(self, pools: List[Pool], coins: List[Coin]):
        self.pools = pools
        self.coins = coins
