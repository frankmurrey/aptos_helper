from typing import Union

from src.schemas.base import TransferBase


class LiqSwSwapConfigSchema(TransferBase):
    module_name: str = "liquidityswap_swap"
    coin_to_swap: Union[str, None] = ""
    coin_to_receive: Union[str, None] = ""
    send_all_balance: Union[bool, str] = False
    slippage: Union[int, float, str] = 0
