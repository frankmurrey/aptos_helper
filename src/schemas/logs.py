from typing import Union
from src import enums

from pydantic import BaseModel


class WalletActionSchema(BaseModel):
    module_name: enums.ModuleName = None
    module_type: enums.ModuleType = None

    date_time: str = None
    wallet_address: str = None
    proxy: Union[str, None] = None
    is_success: Union[bool, None] = None
    status: str = None
    transaction_hash: str = None
