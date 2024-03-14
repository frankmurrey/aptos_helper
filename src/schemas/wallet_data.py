from typing import Optional
from uuid import UUID, uuid4


from pydantic import BaseModel
from pydantic import Field
from pydantic import validator
from aptos_sdk.account import Account, AccountAddress

from src import enums
from src import exceptions
from src.schemas.proxy_data import ProxyData
from utils.proxy import parse_proxy_data
import config


class WalletData(BaseModel):
    index: int = -1

    name: Optional[str] = None
    private_key: str
    pair_address: Optional[str] = None
    proxy: Optional[ProxyData] = None
    wallet_id: UUID = Field(default_factory=uuid4)
    wallet_status: enums.WalletStatus = enums.WalletStatus.inactive

    @validator("proxy", pre=True)
    def validate_proxy(cls, v):
        if isinstance(v, str):
            return parse_proxy_data(proxy_str=v)
        return v

    @validator("private_key", pre=True)
    def validate_private_key(cls, v):
        if not v:
            raise exceptions.AppValidationError(f"Private key is required")

        if len(v) != config.APTOS_KEY_LENGTH:
            raise exceptions.AppValidationError("Private key must be 66 characters long")

        return v

    @property
    def address(self) -> str:
        return str(Account.load_key(self.private_key).address())
