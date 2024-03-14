import random
from typing import Union, TYPE_CHECKING

from aptos_sdk.transactions import EntryFunction, TransactionArgument, Serializer
from aptos_sdk.account import Account, AccountAddress
from loguru import logger

from modules.base import ModuleBase
from contracts.tokens.main import Tokens
from src import enums
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.action_models import TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks import DelegateTask
    from src.schemas.wallet_data import WalletData


class Delegate(ModuleBase):
    DELEGATION_POOL_ADDRESS = "0x1::delegation_pool"
    MIN_DELEGATION_AMOUNT_DECIMALS = 11

    def __init__(
            self,
            account: Account,
            task: 'DelegateTask',
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

        self.account = account
        self.task = task

        self.coin_x = Tokens().get_by_name("Aptos")

    def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        wallet_token_balance_wei = self.get_wallet_token_balance(
            wallet_address=self.account.address(),
            token_address=self.coin_x.contract_address
        )

        if wallet_token_balance_wei == 0:
            logger.error(
                f"Wallet token balance is 0: "
                f"{wallet_token_balance_wei} {self.coin_x.symbol.upper}"
            )
            return None

        src_coin_decimals = self.get_token_decimals(self.coin_x)
        wallet_token_balance_decimals = wallet_token_balance_wei / 10 ** src_coin_decimals

        min_delegation_amount = self.MIN_DELEGATION_AMOUNT_DECIMALS * 10 ** src_coin_decimals

        if wallet_token_balance_wei < min_delegation_amount:
            logger.error(
                f"Wallet token balance is less than min delegation amount (11): "
                f"{wallet_token_balance_decimals} {self.coin_x.symbol.upper()}"
            )
            return None

        coin_x_decimals = self.get_token_decimals(self.coin_x)
        amount_out = random.randint(
            self.task.min_amount_out * 10 ** coin_x_decimals,
            self.task.max_amount_out * 10 ** coin_x_decimals
        )

        if amount_out > wallet_token_balance_wei:
            logger.error(
                f"Amount out is greater than wallet token balance: "
                f"{self.task.max_amount_out * 10 ** coin_x_decimals} > {wallet_token_balance_decimals}"
            )
            return None

        validator_address = AccountAddress.from_hex(self.task.validator_address)

        transaction_args = [
            TransactionArgument(validator_address, Serializer.struct),
            TransactionArgument(int(amount_out), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.DELEGATION_POOL_ADDRESS}",
            "add_stake",
            [],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out / 10 ** coin_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = (
            f"Delegation (Add stake) - "
            f"{round(txn_payload_data.amount_x_decimals, 4)} ({self.coin_x.symbol.upper()}),"
            f" validator address: {self.task.validator_address}."
        )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )

        return txn_status


