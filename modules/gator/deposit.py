from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.gator.base import GatorBase
from modules.base import SingleCoinModuleBase

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from contracts.tokens import Tokens


if TYPE_CHECKING:
    from src.schemas.tasks import GatorDepositTask
    from src.schemas.wallet_data import WalletData


class GatorDeposit(GatorBase, SingleCoinModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'GatorDepositTask',
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

    def send_account_create_txn(self) -> ModuleExecutionResult:
        args = [
            TransactionArgument(7, Serializer.u64),
            TransactionArgument(0, Serializer.u64),
        ]

        coin_y = Tokens().get_by_name("usdc")

        types = [
            TypeTag(StructTag.from_str(self.coin_x.contract_address)),
            TypeTag(StructTag.from_str(coin_y.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::user",
            "register_market_account",
            types,
            args
        )

        return self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=payload,
            txn_info_message="Create trade account"
        )

    def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        """
        Build transaction payload for depositing to trade account
        Returns:

        """
        amount_out_wei = self.calculate_amount_out_from_balance(self.coin_x)
        if amount_out_wei is None:
            logger.error(f"Failed to calculate amount out from balance")
            return None

        amount_out_decimals = amount_out_wei / (10 ** self.token_x_decimals)

        args = [
            TransactionArgument(7, Serializer.u64),
            TransactionArgument(0, Serializer.u64),
            TransactionArgument(int(amount_out_wei), Serializer.u64),
        ]

        types = [
            TypeTag(StructTag.from_str(self.coin_x.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::user",
            "deposit_from_coinstore",
            types,
            args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        account_exists = self.market_account_exists()
        if not account_exists:
            account_creation_result = self.send_account_create_txn()

            if account_creation_result.execution_status == enums.ModuleExecutionStatus.ERROR:
                logger.error(f"Failed to create trade account")
                return account_creation_result

        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Deposit (Gator) - {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status
