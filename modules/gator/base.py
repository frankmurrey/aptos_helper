from typing import TYPE_CHECKING, Union

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from loguru import logger

from modules.base import ModuleBase
from modules.gator.types import MarketData

if TYPE_CHECKING:
    from src.schemas.tasks import GatorTradeTask
    from src.schemas.tasks import GatorDepositTask
    from src.schemas.tasks import GatorWithdrawTask
    from src.schemas.wallet_data import WalletData


class GatorBase(ModuleBase):
    MARKET_TOKEN_DECIMALS = 3

    def __init__(
            self,
            account: Account,
            task: Union['GatorTradeTask', 'GatorDepositTask', 'GatorWithdrawTask'],
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies,
            wallet_data=wallet_data
        )

        self.account = account
        self.task = task

        self.router_address = AccountAddress.from_hex(
            "0xc0deb00c405f84c85dc13442e305df75d1288100cdd82675695f6148c7ece51c"
        )

    def get_user_market_account(self) -> Union[MarketData, None]:
        args = [
            self.account.address().hex(),
            '7',
            '0'
        ]
        response = self.make_view_call(
            function=f"{self.router_address.hex()}::user::get_market_account",
            type_arguments=[],
            arguments=args
        )

        if response is None:
            logger.error(f"Failed to fetch user market account")
            return None

        return MarketData(**response[0])

    def market_account_exists(self) -> Union[bool, None]:
        args = [
            self.account.address().hex(),
            '7',
            '0'
        ]
        response = self.make_view_call(
            function=f"{self.router_address.hex()}::user::has_market_account",
            type_arguments=[],
            arguments=args
        )

        if response is False:
            logger.error(f"Trade account does not exist")
            return False

        if response is None:
            logger.error(f"Failed to check if trade account exists")
            return False

        return True
