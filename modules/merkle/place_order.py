import time
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.merkle import types
from modules.merkle.base import MerkleModuleBase
from modules.merkle.math import calculate_leverage
from modules.merkle.math import calculate_price_impact
from modules.merkle.math import calculate_market_skew

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from utils.delay import get_delay


if TYPE_CHECKING:
    from src.schemas.tasks import MerklePlaceCancelOrderTask
    from src.schemas.tasks import MerklePlaceOpenOrderTask
    from src.schemas.wallet_data import WalletData


class MerklePlaceOpenOrder(MerkleModuleBase):

    def __init__(
            self,
            account: Account,
            task: 'MerklePlaceOpenOrderTask',
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

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            return None
        fee = self.LONG_FEE_PERCENT if self.task.order_type == enums.OrderType.LONG else self.SHORT_FEE_PERCENT
        amount_out_wei_after_fee = int(amount_out_wei * (1 - fee / 100))

        amount_out_decimals = amount_out_wei / 10 ** self.token_x_decimals
        leverage = calculate_leverage(amount_out_decimals, self.MIN_PAY_USD)
        size_delta_wei = int(amount_out_wei_after_fee * leverage)
        is_long = self.task.order_type == enums.OrderType.LONG
        is_increase = True
        is_market = True
        stop_loss_trigger = 0 if self.task.order_type == enums.OrderType.LONG else 18446744073709551615

        pair_info = self.get_pair_info()
        if pair_info is None:
            logger.error("Error getting pair info")
            return None

        pair_state = self.get_pair_state()
        if pair_state is None:
            logger.error("Error getting pair state")
            return None

        market_skew = calculate_market_skew(
            long_open_interest=pair_state.long_open_interest,
            short_open_interest=pair_state.short_open_interest
        )

        price_impact = calculate_price_impact(
            market_skew=market_skew,
            size_delta=size_delta_wei,
            skew_factor=pair_info.skew_factor
        )

        size_delta_after_price_impact = size_delta_wei + (size_delta_wei * price_impact)

        market_price = self.get_market_apt_price(
            pair_info=pair_info,
            pair_state=pair_state
        )
        price_wei = int(market_price * 10 ** 10)
        price_wei_after_slippage = int(price_wei * (1 + (self.task.slippage / 100)))
        take_profit_trigger = int(price_wei * 1.1 if is_long else price_wei * 0.9)
        can_execute_above_price = False
        referrer = self.REF_ADDR if self.task.use_referral else "0x0"
        referrer = AccountAddress.from_hex(referrer)

        if self.task.pseudo_order:
            price_wei_after_slippage = price_wei_after_slippage * 0.8
            # Order will not be executed due price is lower than market price
            # But execution txn will be sent

        args = [
            TransactionArgument(int(size_delta_after_price_impact), Serializer.u64),
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
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
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

        if self.task.reverse_action is True:
            logger.info(f"Waiting 4 seconds before reverse action")
            time.sleep(4)

            order_type = enums.OrderType.SHORT if self.task.order_type == enums.OrderType.LONG else enums.OrderType.LONG
            old_task = self.task.dict(exclude={"module_name",
                                               "module_type",
                                               "module"})

            task = self.task.reverse_action_task(**old_task)

            reverse_action = MerklePlaceCancelOrder(
                account=self.account,
                task=task,
                base_url=self.base_url,
                wallet_data=self.wallet_data,
            )
            reverse_txn_status = reverse_action.send_txn()
            return reverse_txn_status

        return txn_status


class MerklePlaceCancelOrder(MerkleModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'MerklePlaceCancelOrderTask',
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

    def get_account_positions_data(self, order_type: enums.OrderType) -> Union[types.UserPosition, None]:
        try:
            addr = self.SHORT_POSITIONS if order_type == enums.OrderType.SHORT else self.LONG_POSITIONS
            url = f"{self.base_url}/tables/{addr}/item"
            payload = {
                "key_type": "address",
                "value_type": f"{self.router_address.hex()}::trading::Position",
                "key": self.account.address().hex()
            }

            response = self.client.client.post(url=url, json=payload)
            if response.status_code != 200:
                logger.error(f"Error getting account positions data: {response.text}")
                return None

            response_json = response.json()
            return types.UserPosition(**response_json)

        except Exception as e:
            logger.error(f"Error getting account positions data: {e}")
            return None

    def trade_position_wait_loop(self, tries_count: int = 10) -> Union[types.UserPosition, None]:
        """
        Wait for user position data to be updated after order execution
        Args:
            tries_count:
        Returns:

        """
        counter = 0
        logger.info(f"Waiting for user position data to be updated after order execution")
        while counter < tries_count:
            user_position_data = self.get_account_positions_data(order_type=self.task.order_type)
            if user_position_data is None:
                continue

            if int(user_position_data.collateral) != 0:
                logger.info(f"Position found after {counter} tries")
                return user_position_data

            counter += 1
            time.sleep(1)

        else:
            logger.error(f"Error getting user position data after {tries_count} tries")
            return None

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        position = self.trade_position_wait_loop()
        if position is None:
            logger.error("Error getting user position data")
            return None

        collateral_wei = position.collateral
        size_delta_wei = position.size

        is_long = self.task.order_type == enums.OrderType.LONG
        is_increase = False
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

        market_price = self.get_market_apt_price(
            pair_info=pair_info,
            pair_state=pair_state
        )
        price_wei = int(market_price * 10 ** 10)
        take_profit_trigger = int(price_wei * 0.9 if is_long else price_wei * 1.1)
        can_execute_above_price = True

        args = [
            TransactionArgument(int(size_delta_wei), Serializer.u64),
            TransactionArgument(int(collateral_wei), Serializer.u64),
            TransactionArgument(int(price_wei), Serializer.u64),
            TransactionArgument(is_long, Serializer.bool),
            TransactionArgument(is_increase, Serializer.bool),
            TransactionArgument(is_market, Serializer.bool),
            TransactionArgument(int(stop_loss_trigger), Serializer.u64),
            TransactionArgument(int(take_profit_trigger), Serializer.u64),
            TransactionArgument(can_execute_above_price, Serializer.bool)
        ]

        types = [
            TypeTag(StructTag.from_str(f"{self.router_address}::pair_types::APT_USD")),
            TypeTag(StructTag.from_str(self.coin_x.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::managed_trading",
            "place_order",
            types,
            args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=0,
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

        txn_info_message = f"Place cancel order (Merkle) - {self.task.order_type.value}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status
