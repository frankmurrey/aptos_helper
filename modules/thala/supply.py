import time
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from utils.delay import get_delay
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums

from modules.base import SingleCoinModuleBase

if TYPE_CHECKING:
    from src.schemas.wallet_data import WalletData
    from src.schemas.tasks import ThalaSupplyTask
    from src.schemas.tasks import ThalaWithdrawTask


class ThalaSupply(SingleCoinModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'ThalaSupplyTask',
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
        self.router_address = self.get_address_from_hex(
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01"
        )

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            return None

        transaction_args = [TransactionArgument(amount_out_wei, Serializer.u64)]
        types = [
            TypeTag(StructTag.from_str(
                f"0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::stability_pool::Crypto"
            ))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::stability_pool_scripts",
            "deposit_mod",
            types,
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.initial_balance_x_wei is None or self.token_x_decimals is None:
            return self.module_execution_result

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Supply (Thala) - {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        ex_status = txn_status.execution_status

        if ex_status != enums.ModuleExecutionStatus.SUCCESS and ex_status != enums.ModuleExecutionStatus.SENT:
            return txn_status

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            old_task = self.task.dict(exclude={"module_name",
                                               "module_type",
                                               "module"})

            task = self.task.reverse_action_task(**old_task)

            reverse_action = ThalaWithdraw(
                account=self.account,
                task=task,
                base_url=self.base_url,
                wallet_data=self.wallet_data,
            )
            reverse_txn_status = reverse_action.send_txn()
            return reverse_txn_status

        return txn_status


class ThalaWithdraw(SingleCoinModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'ThalaWithdrawTask',
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
        self.router_address = self.get_address_from_hex(
            "0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01"
        )

    def get_supply_amount(self) -> Union[int, None]:
        url = f"{self.base_url}/view"

        payload = {
            "function": f"{self.router_address.hex()}::stability_pool::account_deposit",
            "type_arguments": [
                f"{self.router_address.hex()}::stability_pool::Crypto"
            ],
            "arguments": [
                self.account.address().hex()
            ],
        }
        response = self.client.client.post(url=url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to get supply amount: {response.text}")
            return None

        return int(response.json()[0])

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_in_wei = self.get_supply_amount()
        if amount_in_wei is None:
            logger.error("Failed to get supply amount")
            return None

        transaction_args = [
            TransactionArgument(amount_in_wei, Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::stability_pool_scripts",
            "withdraw_mod",
            [
                TypeTag(StructTag.from_str(f"{self.router_address.hex()}::stability_pool::Crypto"))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_in_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        txn_payload = self.build_transaction_payload()
        if txn_payload is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Withdraw (Thala) - {txn_payload.amount_x_decimals} {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload.payload,
            txn_info_message=txn_info_message
        )

        return txn_status
