import time
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger


from modules.sushi.math import get_amount_in
from modules.sushi.utils import coins_sorted
from modules.base import SwapModuleBase

from utils.delay import get_delay
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums


if TYPE_CHECKING:
    from src.schemas.tasks import SushiSwapTask
    from src.schemas.wallet_data import WalletData


class SushiSwap(SwapModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'SushiSwapTask',
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
            "0x31a6675cbe84365bf2b0cbce617ece6c47023ef70826533bde5203d32171dc3c"
        )

    def get_token_pair_reserve(
            self,
            coin_x_address: str,
            coin_y_address: str
    ) -> Union[tuple[int, int], None]:
        """
        Get token pair reserve
        Args:
        coin_x_address:
        coin_y_address:

        Returns:

        """
        r_addr = self.router_address
        try:
            resource = self.client.account_resource(
                r_addr,
                f"{r_addr.hex()}::swap::TokenPairReserve<{coin_x_address}, {coin_y_address}>"

            )

            res_x = int(resource["data"]["reserve_x"])
            res_y = int(resource["data"]["reserve_y"])
            return res_x, res_y

        except Exception as e:
            logger.error(f"Error getting token pair reserve")
            return None

    def get_sorted_reserves(self) -> Union[tuple[int, int], None]:
        """
        Get sorted reserves
        Returns:

        """
        sorted = coins_sorted(self.coin_x.contract_address, self.coin_y.contract_address)
        if not sorted:
            reserves = self.get_token_pair_reserve(
                coin_x_address=self.coin_y.contract_address,
                coin_y_address=self.coin_x.contract_address
            )
            if reserves is None:
                logger.error("Error getting token pair reserve")
                return None

            res_y, res_x = reserves

        else:
            reserves = self.get_token_pair_reserve(
                coin_x_address=self.coin_x.contract_address,
                coin_y_address=self.coin_y.contract_address
            )
            if reserves is None:
                logger.error("Error getting token pair reserve")
                return None

            res_x, res_y = reserves

        return res_x, res_y

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            return None

        sorted_reserves = self.get_sorted_reserves()
        if sorted_reserves is None:
            logger.error("Error getting sorted reserves")
            return None

        res_x, res_y = sorted_reserves
        amount_in_wei = get_amount_in(
            amount_out=amount_out_wei,
            reserve_out=res_x,
            reserve_in=res_y
        )
        if amount_in_wei is None:
            return None

        amount_in_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

        transaction_args = [
            TransactionArgument(int(amount_out_wei), Serializer.u64),
            TransactionArgument(int(amount_in_with_slippage), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::router",
            "swap_exact_input",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in_wei / 10 ** self.token_y_decimals
        )

    def build_reverse_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        wallet_y_balance_wei = self.get_wallet_token_balance(
            wallet_address=self.account.address(),
            token_address=self.coin_y.contract_address
        )

        if wallet_y_balance_wei == 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance = 0")
            return None

        if self.initial_balance_y_wei is None:
            logger.error(f"Error while getting initial balance of {self.coin_y.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_y_wei
        if amount_out_y_wei <= 0:
            logger.error(f"Wallet {self.coin_y.symbol.upper()} balance less than initial balance")
            return None

        sorted_reserves = self.get_sorted_reserves()
        if sorted_reserves is None:
            logger.error("Error getting sorted reserves")
            return None

        res_x, res_y = sorted_reserves
        amount_in_x_wei = get_amount_in(
            amount_out=amount_out_y_wei,
            reserve_out=res_y,
            reserve_in=res_x
        )
        if amount_in_x_wei is None:
            return None

        amount_in_x_with_slippage_wei = int(amount_in_x_wei * (1 - (self.task.slippage / 100)))

        transaction_args = [
            TransactionArgument(int(amount_out_y_wei), Serializer.u64),
            TransactionArgument(int(amount_in_x_with_slippage_wei), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::router",
            "swap_exact_input",
            [
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(self.coin_x.contract_address))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_y_wei / 10 ** self.token_y_decimals,
            amount_y_decimals=amount_in_x_wei / 10 ** self.token_x_decimals
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

        txn_status = self.send_swap_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )

        ex_status = txn_status.execution_status

        if ex_status != enums.ModuleExecutionStatus.SUCCESS and ex_status != enums.ModuleExecutionStatus.SENT:
            return txn_status

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            reverse_txn_payload_data = self.build_reverse_transaction_payload()
            if reverse_txn_payload_data is None:
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
                self.module_execution_result.execution_info = "Error while building reverse transaction payload"
                return self.module_execution_result

            reverse_txn_status = self.send_swap_type_txn(
                account=self.account,
                txn_payload_data=reverse_txn_payload_data,
                is_reverse=True
            )

            return reverse_txn_status

        return txn_status
