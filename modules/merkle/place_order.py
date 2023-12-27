import time
import json
from typing import Union, TYPE_CHECKING

import websocket
from aptos_sdk.account import Account
from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.base import SingleCoinModuleBase
from modules.merkle import types
from modules.merkle.math import calculate_leverage
from modules.merkle.math import calculate_market_price
from utils.delay import get_delay
from modules.pancake.math import get_amount_in
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums


if TYPE_CHECKING:
    from src.schemas.tasks import MerklePlaceOrderTask
    from src.schemas.wallet_data import WalletData


class MerklePlaceOrder(SingleCoinModuleBase):
    MIN_PAY_USD = 300
    REF_ADDR = "0x83011465ec892aeed8d7747ac109bb61621d08b2286a58095617ba117e980832"
    PROTOCOL_FEE_PERCENT = 7

    def __init__(
            self,
            account: Account,
            task: 'MerklePlaceOrderTask',
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
            "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06"
        )
        self.ws_url = "wss://api.prod.merkle.trade/v1"

    def get_pair_info(self) -> Union[types.PairInfo, None]:
        try:
            ra = self.router_address.hex()
            res_type = f"{ra}::trading::PairInfo<{ra}::pair_types::APT_USD, {self.coin_x.contract_address}>"
            resource = self.client.account_resource(
                self.router_address.hex(),
                res_type
            )
            return types.PairInfo(**resource["data"])

        except Exception as e:
            logger.error(f"Error getting pair info: {e}")
            return None

    def get_pair_state(self) -> Union[types.PairState, None]:
        try:
            ra = self.router_address.hex()
            res_type = f"{ra}::trading::PairState<{ra}::pair_types::APT_USD, {self.coin_x.contract_address}>"
            resource = self.client.account_resource(
                self.router_address.hex(),
                res_type
            )
            return types.PairState(**resource["data"])

        except Exception as e:
            logger.error(f"Error getting pair state: {e}")
            return None

    def get_price(self) -> Union[float, None]:
        ws = websocket.WebSocket()
        sub_msg_0 = f'{{"type":"sub","key":"account:{self.account.address().hex()}:position_events"}}'
        sub_msg_1 = f'{{"type":"sub","key":"price:APT_USD"}}'

        try:
            ws.connect(self.ws_url)
            ws.send(sub_msg_0)
            time.sleep(0.1)
            ws.send(sub_msg_1)

            while True:
                result = ws.recv()
                result_json = json.loads(result)
                if result_json.get("data"):
                    return float(result_json.get("data").get("price"))

                time.sleep(1)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

        finally:
            ws.close()

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            return None
        amount_out_wei_after_fee = int(amount_out_wei * (1 - self.PROTOCOL_FEE_PERCENT / 100))

        amount_out_decimals = amount_out_wei / 10 ** self.token_x_decimals
        leverage = calculate_leverage(amount_out_decimals, self.MIN_PAY_USD)
        size_delta_wei = amount_out_wei_after_fee * leverage
        is_long = self.task.order_type == enums.OrderType.LONG
        is_increase = True
        is_market = True
        stop_loss_trigger = 0

        pair_info = self.get_pair_info()
        if pair_info is None:
            logger.error("Error getting pair info")
            return None

        pair_state = self.get_pair_state()
        if pair_state is None:
            logger.error("Error getting pair state")
            return None

        price_decimals = self.get_price()
        if price_decimals is None:
            logger.error("Error getting price")
            return None

        market_price = calculate_market_price(
            price_decimals=price_decimals,
            long_open_interest=pair_state.long_open_interest,
            short_open_interest=pair_state.short_open_interest,
            skew_factor=pair_info.skew_factor
        )
        price_wei = int(market_price * 10 ** 10)
        price_wei_after_slippage = int(price_wei * (1 + (self.task.slippage / 100)))
        take_profit_trigger = int(price_wei * 1.1 if is_long else price_wei * 0.9)
        can_execute_above_price = False
        referrer = self.REF_ADDR if self.task.use_referral else "0x0"
        referrer = AccountAddress.from_hex(referrer)

        args = [
            TransactionArgument(int(size_delta_wei), Serializer.u64),
            TransactionArgument(int(amount_out_wei), Serializer.u64),
            TransactionArgument(int(price_wei_after_slippage), Serializer.u64),
            TransactionArgument(is_long, Serializer.bool),
            TransactionArgument(is_increase, Serializer.bool),
            TransactionArgument(is_market, Serializer.bool),
            TransactionArgument(int(stop_loss_trigger), Serializer.u64),
            TransactionArgument(int(take_profit_trigger), Serializer.u64),
            TransactionArgument(can_execute_above_price, Serializer.bool),
            TransactionArgument(referrer, Serializer.struct)
        ]

        types = [
            TypeTag(StructTag.from_str(f"{self.router_address}::pair_types::APT_USD")),
            TypeTag(StructTag.from_str(self.coin_x.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::managed_trading",
            "place_order_with_referrer",
            types,
            args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_decimals,
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

        txn_info_message = f"Place Order (Merkle) - {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        ex_status = txn_status.execution_status

        if ex_status != enums.ModuleExecutionStatus.SUCCESS and ex_status != enums.ModuleExecutionStatus.SENT:
            return txn_status

        # if self.task.reverse_action is True:
        #     delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
        #     logger.info(f"Waiting {delay} seconds before reverse action")
        #     time.sleep(delay)
        #
        #     old_task = self.task.dict(exclude={"module_name",
        #                                        "module_type",
        #                                        "module"})
        #
        #     task = self.task.reverse_action_task(**old_task)
        #
        #     reverse_action = ThalaWithdraw(
        #         account=self.account,
        #         task=task,
        #         base_url=self.base_url,
        #         wallet_data=self.wallet_data,
        #     )
        #     reverse_txn_status = reverse_action.send_txn()
        #     return reverse_txn_status

        return txn_status
