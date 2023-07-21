from typing import Union

from src.schemas.base import TransferBase


class ThalaAddLiquidityConfigSchema(TransferBase):
    module_name: str = "thala_add_liquidity"
    coin_x: str = ""
    coin_y: str = ""
    send_all_balance: Union[bool, str] = False


class ThalaRemoveLiquidityConfigSchema(TransferBase):
    module_name: str = "thala_remove_liquidity"
    coin_x: str = ""
    coin_y: str = ""
    send_all_balance: Union[bool, str] = True


class ThalaStakeConfigSchema(TransferBase):
    module_name: str = "thala_stake"
    coin_x: str = ""
    coin_y: str = ""

