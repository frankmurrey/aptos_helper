from typing import Union

from pydantic import BaseModel


class TransferBase(BaseModel):
    min_amount_out: Union[int, float, str] = 0
    max_amount_out: Union[int, float, str] = 0
    min_delay_sec: Union[int, str] = 0
    max_delay_sec: Union[int, str] = 0
    gas_price: Union[int, str] = 0
    gas_limit: Union[int, str] = 0
    wait_for_receipt: Union[bool, str] = False
    txn_wait_timeout_sec: Union[int, str] = 60
    shuffle_wallets: Union[bool, str] = False
    test_mode: Union[bool, str] = True

