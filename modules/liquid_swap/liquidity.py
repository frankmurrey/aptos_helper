import time
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.base import LiquidityModuleBase
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums
from utils.delay import get_delay
from modules.liquid_swap.math import get_optimal_liquidity_amount
from modules.liquid_swap.math import calc_output_burn_liquidity
from modules.liquid_swap.math import d


if TYPE_CHECKING:
    from src.schemas.tasks import LiquidSwapAddLiquidityTask
    from src.schemas.tasks import LiquidSwapRemoveLiquidityTask
    from src.schemas.wallet_data import WalletData


class LiquidityBase(LiquidityModuleBase):
    def __init__(
            self,
            account: Account,
            task: Union['LiquidSwapAddLiquidityTask', 'LiquidSwapRemoveLiquidityTask'],
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
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12"
        )

        self.resource_data = None

    def get_token_pair_reserve(self) -> Union[dict, None]:
        resource_acc_address = self.get_address_from_hex(
            "0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948")
        res_payload = f"{self.router_address}::liquidity_pool::LiquidityPool" \
                      f"<{self.coin_x.contract_address}, {self.coin_y.contract_address}, {self.router_address}::curves::Stable>"

        resource_data = self.get_token_reserve(
            resource_address=resource_acc_address,
            payload=res_payload
        )

        if resource_data is False:
            logger.error("Error getting token pair reserve")
            return None

        if resource_data is not None:
            self.resource_data = resource_data

            reserve_x = resource_data["data"]["coin_x_reserve"]["value"]
            reserve_y = resource_data["data"]["coin_y_reserve"]["value"]

            return {self.coin_x.contract_address: reserve_x,
                    self.coin_y.contract_address: reserve_y}
        else:
            logger.error(f"({self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}) pool does not exist. "
                         f"Try reverse pool ({self.coin_y.symbol.upper()}-{self.coin_x.symbol.upper()}).")
            return None

    def get_lp_supply(
            self,
            lp_token_address: str
    ):
        token_info = self.client.account_resource(
            AccountAddress.from_hex("0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948"),
            f"0x1::coin::CoinInfo<{lp_token_address}>"
        )
        lp_supply = token_info.get("data").get("supply").get("vec")[0].get("integer").get("vec")[0].get("value")

        return lp_supply


class LiquidSwapAddLiquidity(LiquidityBase):
    def __init__(
            self,
            account: Account,
            task: 'LiquidSwapAddLiquidityTask',
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            wallet_data=wallet_data,
            proxies=proxies
        )

        self.account = account
        self.task = task
        self.router_address = self.get_address_from_hex(
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12"
        )

        self.resource_data = None

    def get_staked_pair_balance(self, wallet_address: str) -> Union[dict, None]:
        url = "https://sentrio-api.pontem.network/api/liq"
        payload = {
            "address": wallet_address,
            "x": self.coin_x.contract_address,
            "y": self.coin_y.contract_address,
            "curve": f"{self.router_address}::curves::Stable"
        }
        response = self.client.client.get(url=url, params=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_amount_y_out(
            self,
            amount_out: int,
            tokens_reserve_data: dict
    ):
        reserve_x = int(tokens_reserve_data[self.coin_x.contract_address])
        reserve_y = int(tokens_reserve_data[self.coin_y.contract_address])

        if reserve_x is None or reserve_y is None:
            return None

        amount_in = get_optimal_liquidity_amount(
            x_desired=d(amount_out),
            x_reserve=d(reserve_x),
            y_reserve=d(reserve_y)
        )

        return amount_in

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        tokens_reserve_data: dict = self.get_token_pair_reserve()
        if tokens_reserve_data is None:
            return None

        if self.initial_balance_x_wei == 0 or self.initial_balance_y_wei == 0:
            logger.error(f"Wallet token balance is 0: "
                         f"{self.initial_balance_x_wei} {self.coin_x.symbol.upper}, "
                         f"{self.initial_balance_y_wei} {self.coin_y.symbol.upper}")
            return None

        amount_out_x = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        amount_out_x_slippage = amount_out_x - (amount_out_x * self.task.slippage / 100)
        amount_out_y = self.get_amount_y_out(
            amount_out=amount_out_x,
            tokens_reserve_data=tokens_reserve_data
        )
        if amount_out_y is None:
            logger.error("Error getting amount out")
            return None

        if amount_out_y == 0:
            logger.error("Amount out is 0")
            return None

        amount_out_y_slippage = int(amount_out_y) - (int(amount_out_y) * self.task.slippage / 100)

        if amount_out_y > self.initial_balance_y_wei:
            logger.error(
                f"Amount out Y is greater than wallet token balance: "
                f"need: {amount_out_y / 10 ** self.token_y_decimals} {self.coin_y.symbol.upper()}, "
                f"balance: {self.initial_balance_y_wei / 10 ** self.token_y_decimals} "
                f"{self.coin_y.symbol.upper()}"
            )
            return None

        transaction_args = [
            TransactionArgument(int(amount_out_x), Serializer.u64),
            TransactionArgument(int(amount_out_x_slippage), Serializer.u64),
            TransactionArgument(int(amount_out_y), Serializer.u64),
            TransactionArgument(int(amount_out_y_slippage), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::scripts_v2",
            "add_liquidity",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(f"{self.router_address}::curves::Stable"))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_x / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_out_y / 10 ** self.token_y_decimals
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

        txn_status = self.send_liquidity_type_txn(
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

            old_task = self.task.dict(exclude={"module_name",
                                               "module_type",
                                               "module"})

            task = self.task.reverse_action_task(**old_task)

            reverse_action = LiquidSwapRemoveLiquidity(
                account=self.account,
                task=task,
                base_url=self.base_url,
                wallet_data=self.wallet_data
            )
            reverse_txn_status = reverse_action.send_txn()
            return reverse_txn_status

        return txn_status


class LiquidSwapRemoveLiquidity(LiquidityBase):
    def __init__(
            self,
            account: Account,
            task: 'LiquidSwapRemoveLiquidityTask',
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None,
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
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12"
        )

        self.resource_data = None

    def get_amounts_out(self, wallet_address: AccountAddress) -> Union[dict, None]:
        token_reserve = self.get_token_pair_reserve()
        if token_reserve is None:
            logger.error(f"Error while fetching token reserve")

        reserve_x = token_reserve.get(self.coin_x.contract_address)
        reserve_y = token_reserve.get(self.coin_y.contract_address)

        if not reserve_x or not reserve_y:
            logger.error(f"Error while fetching token reserve")
            return None

        lp_addr = f"0x5a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948::lp_coin::LP" \
                  f"<{self.coin_x.contract_address}, {self.coin_y.contract_address}, {self.router_address}::curves::Stable>"
        wallet_lp_balance = self.get_wallet_token_balance(
            token_address=lp_addr,
            wallet_address=wallet_address
        )
        lp_supply = self.get_lp_supply(lp_token_address=lp_addr)

        if wallet_lp_balance == 0:
            logger.error(f"Wallet ({self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}) lp coin balance is 0")
            return None

        if not lp_supply:
            logger.error(f"Error while fetching lp supply")
            return None

        lp_burn_output: dict = calc_output_burn_liquidity(
            reserve_x=int(reserve_x),
            reserve_y=int(reserve_y),
            lp_supply=int(lp_supply),
            to_burn=int(wallet_lp_balance)
        )

        out_x_with_slippage = int(lp_burn_output['x'] - (lp_burn_output['x'] * self.task.slippage / 100))
        out_y_with_slippage = int(lp_burn_output['y'] - (lp_burn_output['y'] * self.task.slippage / 100))

        return {
            "to_burn": wallet_lp_balance,
            "amount_out_x": out_x_with_slippage,
            "amount_out_y": out_y_with_slippage
        }

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:

        lp_burn_output = self.get_amounts_out(wallet_address=self.account.address())
        if not lp_burn_output:
            return None

        lp_amount_to_burn = lp_burn_output['to_burn']
        min_amount_x = lp_burn_output['amount_out_x']
        min_amount_y = lp_burn_output['amount_out_y']

        transaction_args = [
            TransactionArgument(int(lp_amount_to_burn), Serializer.u64),
            TransactionArgument(int(min_amount_x), Serializer.u64),
            TransactionArgument(int(min_amount_y), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::scripts_v2",
            "remove_liquidity",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(f"{self.router_address}::curves::Stable"))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=min_amount_x / 10 ** self.token_x_decimals,
            amount_y_decimals=min_amount_y / 10 ** self.token_y_decimals
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

        txn_status = self.send_liquidity_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )
        return txn_status
