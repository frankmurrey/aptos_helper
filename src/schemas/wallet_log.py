from typing import Union

from pydantic import BaseModel


class WalletActionSchema(BaseModel):
    date_time: str = None
    wallet_address: str = None
    proxy: Union[str, None] = None
    is_success: Union[bool, None] = None
    transaction_hash: str = None
    action_type: str = None
    module_name: str = None
