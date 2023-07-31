from pydantic import BaseModel

from typing import Union


class ProxyData(BaseModel):
    host: str
    port: Union[int, str]
    username: str = None
    password: str = None
    auth: bool = False


class WalletData(BaseModel):
    wallet: str
    proxy: Union[ProxyData, None] = None
    evm_pair_address: Union[str, None] = None
