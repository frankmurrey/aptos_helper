from typing import Union, TYPE_CHECKING

from loguru import logger
from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag


from modules.base import SwapModuleBase
from modules.pancake.math import get_amount_in
from src.schemas.action_models import TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks import PancakeSwapTask
    from src.schemas.wallet_data import WalletData


class PancakeSwap(SwapModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'PancakeSwapTask',
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
            "0xc7efb4076dbe143cbcd98cfaaa929ecfc8f299203dfff63b95ccb6bfe19850fa"
        )

    def get_token_pair_reserve(self) -> Union[dict, None]:
        coin_x = self.coin_x.contract_address
        coin_y = self.coin_y.contract_address

        data = self.get_token_reserve(
            resource_address=self.router_address,
            payload=f"{self.router_address}::swap::TokenPairReserve"
                    f"<{coin_x}, {coin_y}>"
        )

        if data is False:
            logger.error("Error getting token pair reserve")
            return None

        if data is not None:
            reserve_x = data["data"]["reserve_x"]
            reserve_y = data["data"]["reserve_y"]

            return {
                coin_x: reserve_x,
                coin_y: reserve_y
            }
        else:

            reversed_data = self.get_token_reserve(
                resource_address=self.router_address,
                payload=f"{self.router_address}::swap::TokenPairReserve"
                        f"<{coin_y}, {coin_x}>"
            )
            if not reversed_data:
                logger.error("Error getting token pair reserve")
                return None

            reserve_x = reversed_data["data"]["reserve_x"]
            reserve_y = reversed_data["data"]["reserve_y"]

            return {
                coin_x: reserve_y,
                coin_y: reserve_x
            }

    def get_amount_in(
            self,
            amount_out: int,
            coin_x_address: str,
            coin_y_address: str
    ) -> Union[int, None]:
        tokens_reserve: dict = self.get_token_pair_reserve()
        if tokens_reserve is None:
            logger.error("Error while getting token pair reserve")
            return None

        reserve_x = int(tokens_reserve[coin_x_address])
        reserve_y = int(tokens_reserve[coin_y_address])

        if reserve_x is None or reserve_y is None:
            logger.error("Error while getting token pair reserve")
            return None

        amount_in = get_amount_in(
            amount_out=amount_out,
            reserve_x=reserve_x,
            reserve_y=reserve_y
        )

        return amount_in

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        if amount_out_wei is None:
            logger.error("Error while calculating amount out")
            return None

        amount_in_wei = self.get_amount_in(
            amount_out=amount_out_wei,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address
        )
        if amount_in_wei is None:
            logger.error("Error while calculating amount in")
            return None

        amount_in_with_slippage = int(amount_in_wei * (1 - (self.task.slippage / 100)))

        amount_out_decimals = amount_out_wei / 10 ** self.token_x_decimals
        amount_in_decimals = amount_in_wei / 10 ** self.token_y_decimals
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
            amount_x_decimals=amount_out_decimals,
            amount_y_decimals=amount_in_decimals
        )

    def build_reverse_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        wallet_y_balance_wei = self.get_wallet_token_balance(
            wallet_address=self.account.address(),
            token_address=self.coin_x.contract_address
        )

        if wallet_y_balance_wei == 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance = 0")
            return None

        if self.initial_balance_x_wei is None:
            logger.error(f"Error while getting initial balance of {self.coin_x.symbol.upper()}")
            return None

        amount_out_y_wei = wallet_y_balance_wei - self.initial_balance_x_wei
        if amount_out_y_wei <= 0:
            logger.error(f"Wallet {self.coin_x.symbol.upper()} balance less than initial balance")
            return None

        amount_in_x_wei = self.get_amount_in(
            amount_out=amount_out_y_wei,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address
        )
        if amount_in_x_wei is None:
            logger.error("Error while calculating amount in")
            return None

        amount_in_x_with_slippage_wei = int(amount_in_x_wei * (1 - (self.task.slippage / 100)))
        amount_out_y_decimals = amount_out_y_wei / 10 ** self.token_x_decimals
        amount_in_x_decimals = amount_in_x_wei / 10 ** self.token_y_decimals

        transaction_args = [
            TransactionArgument(int(amount_out_y_wei), Serializer.u64),
            TransactionArgument(int(amount_in_x_with_slippage_wei), Serializer.u64)
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
            amount_x_decimals=amount_out_y_decimals,
            amount_y_decimals=amount_in_x_decimals
        )
