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
    from src.schemas.tasks import UnlockTask


class Unlock(ModuleBase):
    DELEGATION_POOL_ADDRESS = "0x1::delegation_pool"
    MIN_DELEGATION_AMOUNT_DECIMALS = 11

    def __init__(
            self,
            account: Account,
            task: 'UnlockTask',
            base_url: str,
            proxies: dict = None
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account
        )

        self.account = account
        self.task = task

        self.coin_x = Tokens().get_by_name("Aptos")

    def get_current_staked_balance(
            self,
            wallet_address: AccountAddress,
            validator_address: AccountAddress
    ) -> Union[int, None]:
        url = f"{self.base_url}/view"
        payload = {
            "function": "0x1::delegation_pool::get_stake",
            "type_arguments": [],
            "arguments": [
                str(validator_address),
                str(wallet_address)
            ],
        }
        response = self.client.client.post(url=url, json=payload)
        if response.status_code != 200:
            logger.error(f"Error getting current staked balance: {response.text}")
            return None

        response_json = response.json()

        return int(response_json[0])

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        validator_address = AccountAddress.from_hex(self.task.validator_address)

        current_staked_balance = self.get_current_staked_balance(
            wallet_address=self.account.address(),
            validator_address=validator_address
        )

        if current_staked_balance is None:
            return None

        if current_staked_balance == 0:
            logger.error(f"Current staked balance is 0")
            return None

        amount_in_wei = current_staked_balance

        transaction_args = [
            TransactionArgument(validator_address, Serializer.struct),
            TransactionArgument(int(amount_in_wei), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.DELEGATION_POOL_ADDRESS}",
            "unlock",
            [],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_in_wei / 10 ** self.get_token_decimals(self.coin_x),
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = (
            f"Unlock (Unstake delegation) - "
            f"{round(txn_payload_data.amount_x_decimals, 4)} ({self.coin_x.symbol.upper()}),"
            f" validator address: {self.task.validator_address}."
        )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )

        return txn_status
