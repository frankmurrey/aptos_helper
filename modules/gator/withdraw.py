from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.base import SingleCoinModuleBase
from modules.gator.base import GatorBase

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult


if TYPE_CHECKING:
    from src.schemas.tasks import GatorWithdrawTask
    from src.schemas.wallet_data import WalletData


class GatorWithdraw(GatorBase, SingleCoinModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'GatorWithdrawTask',
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

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        """
        Build transaction payload for depositing to trade account
        Returns:

        """

        market_account = self.get_user_market_account()
        if market_account is None:
            logger.error(f"Failed to fetch user market account")
            return None

        if self.coin_x.symbol.lower() == "aptos":
            amount_out = market_account.base_available

        else:
            amount_out = market_account.quote_available

        args = [
            TransactionArgument(7, Serializer.u64),
            TransactionArgument(int(amount_out), Serializer.u64),
        ]

        types = [
            TypeTag(StructTag.from_str(self.coin_x.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::user",
            "withdraw_to_coinstore",
            types,
            args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out / (10 ** self.token_x_decimals),
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        account_exists = self.market_account_exists()
        if not account_exists:
            err_msg = f"Trade account does not exist, please first make deposit through Deposit module"
            logger.error(err_msg)
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = err_msg

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Withdraw (Gator) - {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status
