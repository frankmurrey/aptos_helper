from typing import Union

from src.schemas.base import TransferBase


class PancakeConfigSchema(TransferBase):
    module_name: str = "pancake"
    coin_to_swap: Union[str, None] = ""
    coin_to_receive: Union[str, None] = ""
    send_all_balance: Union[bool, str] = False
    slippage: Union[int, str] = 0
