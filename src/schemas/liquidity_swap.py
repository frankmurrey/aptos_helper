from typing import Union

from src.schemas.base import TransferBase


class LiqSwSwapConfigSchema(TransferBase):
    module_name: str = "liquidityswap_swap"
    coin_to_swap: Union[str, None] = ""
    coin_to_receive: Union[str, None] = ""
    random_dst_coin: Union[bool, str] = False
    send_all_balance: Union[bool, str] = False
    send_percent_balance: Union[bool, str] = False
    slippage: Union[int, float, str] = 0


class LiqSwAddLiquidityConfigSchema(TransferBase):
    module_name: str = "liquidityswap_add_liquidity"
    coin_x: Union[str, None] = ""
    coin_y: Union[str, None] = ""
    send_all_balance: Union[bool, str] = False
    slippage: Union[int, float, str] = 0.5


class LiqSwRemoveLiquidityConfigSchema(TransferBase):
    module_name: str = "liquidityswap_remove_liquidity"
    coin_x: str = ""
    coin_y: str = ""
    send_all_balance: Union[bool, str] = True
    slippage: Union[int, float, str] = 0.5
