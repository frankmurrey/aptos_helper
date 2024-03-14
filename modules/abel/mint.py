import random
import time
from typing import Union, TYPE_CHECKING, Callable


from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.base import SingleCoinModuleBase
from modules.abel.redeem import AbleFinanceRedeem
from src import enums
from utils.delay import get_delay
from contracts.tokens.main import TokenBase
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.wallet_data import WalletData

if TYPE_CHECKING:
    from src.schemas.tasks import AbelSupplyTask
    from src.schemas.tasks import AbelWithdrawTask


class AbleFinanceMint(SingleCoinModuleBase):
    store_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin::ACoinStore"
    lend_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin_lend"

    def __init__(
            self,
            account: Account,
            task: 'AbelSupplyTask',
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

    def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase,
    ) -> Union[int, None]:
        initial_balance_x_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals

        if self.task.use_all_balance:
            amount_out_wei = self.initial_balance_x_wei

        elif self.task.send_percent_balance:
            percent = random.randint(
                int(self.task.min_amount_out), int(self.task.max_amount_out)
            ) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

        elif initial_balance_x_decimals < self.task.min_amount_out:
            logger.error(
                f"Wallet {coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {initial_balance_x_decimals}, min amount out: {self.task.min_amount_out}"
            )
            return None

        elif initial_balance_x_decimals > self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=initial_balance_x_decimals,
                decimals=self.token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=self.token_x_decimals
            )

        return amount_out_wei

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            return None

        if amount_out_wei > self.initial_balance_x_wei:
            logger.error(f"Amount out {amount_out_wei} > initial balance {self.initial_balance_x_wei}")
            return None

        transaction_args = [
            TransactionArgument(amount_out_wei, Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.lend_address}",
            "mint_entry",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        self.set_fetched_data_to_exec_storage()

        if self.check_local_tokens_data() is False:
            logger.error("Error while checking local tokens data")
            return self.module_execution_result

        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Mint (Abel finance) {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"

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

            reverse_action = AbleFinanceRedeem(
                account=self.account,
                task=task,
                base_url=self.base_url,
                wallet_data=self.wallet_data,
            )
            reverse_txn_status = reverse_action.send_txn()
            return reverse_txn_status

        return txn_status
