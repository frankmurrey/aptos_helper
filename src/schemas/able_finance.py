from typing import Union

from src.schemas.base import TransferBase


class AbleMintConfigSchema(TransferBase):
    module_name: str = "able_mint"
    coin_option: str = ""
    send_all_balance: Union[bool, str] = False


class AbleRedeemConfigSchema(TransferBase):
    module_name: str = "able_redeem"
    coin_option: str = ""
    redeem_all: Union[bool, str] = False
