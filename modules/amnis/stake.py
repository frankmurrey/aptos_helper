from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from loguru import logger

from modules.base import SingleCoinModuleBase

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult

if TYPE_CHECKING:
    from src.schemas.tasks import AmnisMintAndStakeTask
    from src.schemas.wallet_data import WalletData


class AmnisMintAndStake(SingleCoinModuleBase):
    MIN_AMOUNT_OUT_WEI = 2e7

    def __init__(
            self,
            account: Account,
            task: 'AmnisMintAndStakeTask',
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
            "0x111ae3e5bc816a5e63c2da97d0aa3886519e0cd5e4b046659fa35796bd11542a"
        )

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(self.coin_x)
        if not amount_out_wei:
            logger.error(f"Failed to calculate amount out from balance")
            return None

        if amount_out_wei < self.MIN_AMOUNT_OUT_WEI:
            logger.error(f"Amount to mint and stake should be at least {self.MIN_AMOUNT_OUT_WEI / 1e8} APT")
            return None

        args = [
            TransactionArgument(int(amount_out_wei), Serializer.u64),
            TransactionArgument(self.account.address(), Serializer.struct)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::router",
            "deposit_and_stake_entry",
            [],
            args,
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / 1e8,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Mint and Stake (Amnis) - {txn_payload_data.amount_x_decimals} APT"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status
