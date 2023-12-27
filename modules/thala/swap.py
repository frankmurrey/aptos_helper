import time
from typing import Union

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from src.schemas.tasks.base.swap import SwapTaskBase
from utils.delay import get_delay
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums
from src.schemas.wallet_data import WalletData


from modules.base import SwapModuleBase
from modules.thala import utils
from modules.thala.router import build_graph
from modules.thala.router import encode_route
from modules.thala.router import find_route_given_exact_input
from modules.thala.pool_data_client import PoolDataClient


class ThalaSwap(SwapModuleBase):
    def __init__(
            self,
            account: Account,
            task: SwapTaskBase,
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
        self.router_address = self.get_address_from_hex(utils.FJ_PREFIX)

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(self.coin_x)
        if amount_out_wei is None:
            logger.error(f"Failed to calculate amount out for {self.coin_x.symbol}")
            return None

        amount_out_decimals = amount_out_wei / (10 ** self.token_x_decimals)

        cli = PoolDataClient(data_url="https://app.thala.fi/api/pool-balances")
        pool_data = cli.get_pool_data()
        if pool_data is None:
            logger.error(f"Failed to fetch pool data")
            return None

        graph = build_graph(pool_data.pools)
        if graph is None:
            logger.error(f"Failed to build graph")
            return None

        route = find_route_given_exact_input(
            graph=graph,
            start_token=self.coin_x.contract_address,
            end_token=self.coin_y.contract_address,
            amount_in=amount_out_decimals,
            max_hops=1
        )
        if not route:
            logger.error(f"Failed to find route")
            return None

        encoded_route = encode_route(
            route=route,
            slippage_percentage=self.task.slippage,
            token_in_decimals=self.token_x_decimals,
            token_out_decimals=self.token_y_decimals
        )

        transaction_args = [TransactionArgument(arg, Serializer.u64) for arg in encoded_route.args]
        types = [TypeTag(StructTag.from_str(arg_type)) for arg_type in encoded_route.type_args]

        payload = EntryFunction.natural(
            encoded_route.address,
            encoded_route.func_name,
            types,
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=route.amount_in,
            amount_y_decimals=route.amount_out
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

        amount_out_y_wei_decimals = amount_out_y_wei / (10 ** self.token_y_decimals)

        cli = PoolDataClient(data_url="https://app.thala.fi/api/pool-balances")
        pool_data = cli.get_pool_data()
        if pool_data is None:
            logger.error(f"Failed to fetch pool data")
            return None

        graph = build_graph(pool_data.pools)
        if graph is None:
            logger.error(f"Failed to build graph")
            return None

        route = find_route_given_exact_input(
            graph=graph,
            start_token=self.coin_y.contract_address,
            end_token=self.coin_x.contract_address,
            amount_in=amount_out_y_wei_decimals,
            max_hops=1
        )
        if not route:
            logger.error(f"Failed to find route")
            return None

        encoded_route = encode_route(
            route=route,
            slippage_percentage=self.task.slippage,
            token_in_decimals=self.token_y_decimals,
            token_out_decimals=self.token_x_decimals
        )

        transaction_args = [TransactionArgument(arg, Serializer.u64) for arg in encoded_route.args]
        types = [TypeTag(StructTag.from_str(arg_type)) for arg_type in encoded_route.type_args]

        payload = EntryFunction.natural(
            encoded_route.address,
            encoded_route.func_name,
            types,
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=route.amount_in,
            amount_y_decimals=route.amount_out
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
