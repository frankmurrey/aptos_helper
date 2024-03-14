from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from loguru import logger

from modules.base import ModuleBase

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult


if TYPE_CHECKING:
    from src.schemas.tasks import AmnisUnstakeTask
    from src.schemas.wallet_data import WalletData


class AmnisUnstake(ModuleBase):

    def __init__(
            self,
            account: Account,
            task: 'AmnisUnstakeTask',
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

    def get_staked_balance(self) -> Union[int, None]:
        """
        Get staked balance
        Returns:
        int: staked balance
        """
        try:
            staked_balance = self.get_wallet_token_balance(
                wallet_address=self.account.address(),
                token_address=f"{self.router_address.hex()}::stapt_token::StakedApt"
            )
            return staked_balance

        except Exception as e:
            logger.error(f"Failed to fetch staked balance: {e}")
            return None

    def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        staked_balance_wei = self.get_staked_balance()
        if staked_balance_wei is None:
            logger.error(f"Failed to fetch staked balance")
            return None

        if staked_balance_wei == 0:
            logger.error(f"Staked balance is 0")
            return None

        args = [
            TransactionArgument(int(staked_balance_wei), Serializer.u64),
            TransactionArgument(self.account.address(), Serializer.struct)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::router",
            "unstake_entry",
            [],
            args,
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=staked_balance_wei / 1e8,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        """
        Send transaction
        Returns:
        """

        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Unstake (Amnis) - {txn_payload_data.amount_x_decimals} stAPT"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status
