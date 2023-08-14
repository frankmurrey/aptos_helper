from typing import Union

from pydantic import BaseModel

from src.schemas.base import TransferBase


class ClaimConfigSchema(BaseModel):
    module_name: str = "aptos_bridge_claim"
    gas_limit: Union[int, str] = 0
    gas_price: Union[int, str] = 0
    force_gas_limit: Union[bool, str] = False
    min_delay_sec: Union[int, str] = 0
    max_delay_sec: Union[int, str] = 0
    test_mode: bool = True
    wait_for_receipt: bool = False
    txn_wait_timeout_sec: Union[int, str] = 0


class AptosBridgeConfigSchema(TransferBase):
    module_name: str = "aptos_bridge"
    coin_to_bridge: str = ""
    dst_chain_name: str = ""
    send_all_balance: Union[bool, str] = False
