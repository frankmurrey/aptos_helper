import random
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from modules.gator.base import GatorBase
from modules.base import MultiCoinModuleBase

from src import enums
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from contracts.base import TokenBase


if TYPE_CHECKING:
    from src.schemas.tasks import GatorTradeTask
    from src.schemas.wallet_data import WalletData


class GatorTrade(GatorBase, MultiCoinModuleBase):

    def __init__(
            self,
            account: Account,
            task: 'GatorTradeTask',
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

        self.maker_address = AccountAddress.from_hex(
            "0x63e39817ec41fad2e8d0713cc906a5f792e4cd2cf704f8b5fab6b2961281fa11"
        )

    def calculate_amount_out_from_market_balance(
            self,
            coin: TokenBase,
            balance: int,
    ) -> Union[int, None]:
        """"
        Calculate amount out of market balance
        """
        initial_balance_x_decimals = self.initial_balance_x_wei / 10 ** self.MARKET_TOKEN_DECIMALS

        if balance == 0:
            logger.error(f"Wallet {coin.symbol.upper()} balance = 0")
            return None

        use_all_balance = getattr(self.task, "use_all_balance", None)
        send_percent_balance = getattr(self.task, "send_percent_balance", None)
        min_amount_out = getattr(self.task, "min_amount_out", None)
        max_amount_out = getattr(self.task, "max_amount_out", None)

        if use_all_balance:
            amount_out_wei = balance

        elif send_percent_balance:
            percent = random.randint(
                int(min_amount_out), int(max_amount_out)
            ) / 100
            amount_out_wei = int(balance * percent)

        elif initial_balance_x_decimals < min_amount_out:
            logger.error(
                f"Wallet {coin.symbol.upper()} balance less than min amount out, "
                f"balance: {initial_balance_x_decimals}, min amount out: {min_amount_out}"
            )
            return None

        elif initial_balance_x_decimals < max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=initial_balance_x_decimals,
                decimals=self.MARKET_TOKEN_DECIMALS
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=max_amount_out,
                decimals=self.MARKET_TOKEN_DECIMALS
            )

        return amount_out_wei

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        market_account = self.get_user_market_account()
        if market_account is None:
            logger.error(f"Failed to fetch trade account")
            return None

        if self.coin_x.symbol == "aptos":
            market_balance_x = market_account.base_available

        else:
            market_balance_x = market_account.quote_available

        amount_out_wei = self.calculate_amount_out_from_market_balance(
            coin=self.coin_x,
            balance=market_balance_x
        )
        if amount_out_wei is None:
            logger.error(f"Failed to calculate amount out from balance")
            return None

        if amount_out_wei < 0.5 * (10 ** self.MARKET_TOKEN_DECIMALS) and self.coin_x.symbol == "aptos":
            logger.error(f"Minimum order size is 0.5 APT")
            return None

        args = [
            TransactionArgument(7, Serializer.u64),
            TransactionArgument(self.maker_address, Serializer.struct),
            TransactionArgument(True, Serializer.bool),
            TransactionArgument(int(amount_out_wei), Serializer.u64),
            TransactionArgument(3, Serializer.u8),
        ]

        types = [
            TypeTag(StructTag.from_str(self.coin_x.contract_address)),
            TypeTag(StructTag.from_str(self.coin_y.contract_address))
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::market",
            "place_market_order_user_entry",
            types,
            args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / (10 ** self.MARKET_TOKEN_DECIMALS),
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        account_exists = self.market_account_exists()
        if not account_exists:
            err_msg = f"Trade account does not exist, please first make deposit through Deposit module"
            logger.error(err_msg)
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = err_msg

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = (f"Market Order (Gator) - {txn_payload_data.amount_x_decimals} {self.coin_x.symbol.upper()}"
                            f" → {self.coin_y.symbol.upper()}")

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )
        return txn_status


