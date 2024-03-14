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
from modules.liquid_swap.math import get_coins_out_with_fees_stable
from modules.liquid_swap.math import get_coins_out_with_fees
from modules.liquid_swap.math import d


class LiquidSwapSwap(SwapModuleBase):
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
        self.router_address = self.get_address_from_hex(
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12"
        )

        self.resource_data = None
        self.pool_type = None

    def get_token_pair_reserve(self, pool_type: str) -> Union[dict, None]:
        coin_x = self.coin_x.contract_address
        coin_y = self.coin_y.contract_address

        resource_acc_address = self.get_address_from_hex(
            "0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948"
        )

        res_payload = f"{self.router_address}::liquidity_pool::LiquidityPool" \
                      f"<{coin_x}, {coin_y}, {self.router_address}::curves::{pool_type}>"

        resource_data = self.get_token_reserve(
            resource_address=resource_acc_address,
            payload=res_payload
        )

        if resource_data is not None:
            self.resource_data = resource_data

            reserve_x = resource_data["data"]["coin_x_reserve"]["value"]
            reserve_y = resource_data["data"]["coin_y_reserve"]["value"]

            return {
                coin_x: reserve_x,
                coin_y: reserve_y
            }

        else:

            res_payload = f"{self.router_address}::liquidity_pool::LiquidityPool" \
                          f"<{coin_y}, {coin_x}, {self.router_address}::curves::{pool_type}>"

            reversed_data = self.get_token_reserve(
                resource_address=resource_acc_address,
                payload=res_payload
            )
            if reversed_data is None:
                logger.error(f"Error getting token pair reserve (reverse), {pool_type} pool")
                return None

            self.resource_data = reversed_data
            reserve_x = reversed_data["data"]["coin_x_reserve"]["value"]
            reserve_y = reversed_data["data"]["coin_y_reserve"]["value"]

            return {
                coin_x: reserve_y,
                coin_y: reserve_x
            }

    def get_amount_in_stable_pool(
            self,
            amount_out: int,
            coin_x_address: str,
            coin_y_address: str,
            coin_x_decimals: int,
            coin_y_decimals: int
    ) -> Union[int, None]:
        tokens_reserve: dict = self.get_token_pair_reserve(pool_type="Stable")
        if tokens_reserve is None:
            logger.error(f"Error getting token pair reserve, Stable pool")
            return None

        reserve_x = int(tokens_reserve[coin_x_address])
        reserve_y = int(tokens_reserve[coin_y_address])

        if reserve_x is None or reserve_y is None:
            logger.error(f"Error getting token pair reserve, Stable pool")
            return None

        pool_fee = int(self.resource_data["data"]["fee"])

        amount_in = get_coins_out_with_fees_stable(
            coin_in=d(amount_out),
            reserve_in=d(reserve_x),
            reserve_out=d(reserve_y),
            scale_in=d(pow(10, coin_x_decimals)),
            scale_out=d(pow(10, coin_y_decimals)),
            fee=d(pool_fee)
        )

        return int(amount_in)

    def get_amount_in_uncorrelated_pool(
            self,
            amount_out: int,
            coin_x_address: str,
            coin_y_address: str,
    ) -> Union[int, None]:
        tokens_reserve: dict = self.get_token_pair_reserve(pool_type="Uncorrelated")

        if tokens_reserve is None:
            logger.error(f"Error getting token pair reserve, Uncorrelated pool")
            return None

        reserve_x = int(tokens_reserve[coin_x_address])
        reserve_y = int(tokens_reserve[coin_y_address])

        if reserve_x is None or reserve_y is None:
            logger.error(f"Error getting token pair reserve, Uncorrelated pool")
            return None

        pool_fee = int(self.resource_data["data"]["fee"])

        amount_in = get_coins_out_with_fees(
            coin_in_val=d(amount_out),
            reserve_in=d(reserve_x),
            reserve_out=d(reserve_y),
            fee=d(pool_fee)
        )

        return amount_in

    def get_most_profitable_amount_in_and_set_pool_type(
            self,
            amount_out: int,
            coin_x_address: str,
            coin_y_address: str,
            coin_x_decimals: int,
            coin_y_decimals: int
    ):
        stable_pool_amount_in = self.get_amount_in_stable_pool(
            amount_out=amount_out,
            coin_x_address=coin_x_address,
            coin_y_address=coin_y_address,
            coin_x_decimals=coin_x_decimals,
            coin_y_decimals=coin_y_decimals
        )

        if stable_pool_amount_in is None:
            logger.error(f"Error while getting amount in, Stable pool")
            return None

        uncorrelated_pool_amount_in = self.get_amount_in_uncorrelated_pool(
            amount_out=amount_out,
            coin_x_address=coin_x_address,
            coin_y_address=coin_y_address
        )

        if uncorrelated_pool_amount_in is None:
            logger.error(f"Error while getting amount in, Uncorrelated pool")
            return None

        if stable_pool_amount_in > uncorrelated_pool_amount_in:
            self.pool_type = "Stable"
            return stable_pool_amount_in

        self.pool_type = "Uncorrelated"
        return uncorrelated_pool_amount_in

    def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        amount_out_wei = self.calculate_amount_out_from_balance(coin_x=self.coin_x)
        amount_in_wei = self.get_most_profitable_amount_in_and_set_pool_type(
            amount_out=amount_out_wei,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
            coin_x_decimals=self.token_x_decimals,
            coin_y_decimals=self.token_y_decimals
        )

        if amount_out_wei is None or amount_in_wei is None:
            logger.error(f"Error while building transaction payload")
            return None

        amount_out_decimals = amount_out_wei / 10 ** self.token_x_decimals
        amount_in_decimals = amount_in_wei / 10 ** self.token_y_decimals

        transaction_args = [
            TransactionArgument(int(amount_out_wei), Serializer.u64),
            TransactionArgument(int(amount_in_wei), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::scripts_v2",
            "swap",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(f"{self.router_address}::curves::{self.pool_type}"))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_decimals,
            amount_y_decimals=amount_in_decimals
        )

    def build_reverse_txn_payload_data(self):
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

        amount_in_x_wei = self.get_most_profitable_amount_in_and_set_pool_type(
            amount_out=amount_out_y_wei,
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
            coin_x_decimals=self.token_x_decimals,
            coin_y_decimals=self.token_y_decimals
        )
        if amount_in_x_wei is None:
            return None

        amount_out_y_decimals = amount_out_y_wei / 10 ** self.token_x_decimals
        amount_in_x_decimals = amount_in_x_wei / 10 ** self.token_y_decimals

        transaction_args = [
            TransactionArgument(int(amount_out_y_wei), Serializer.u64),
            TransactionArgument(int(amount_in_x_wei), Serializer.u64)
        ]
        payload = EntryFunction.natural(
            f"{self.router_address}::scripts_v2",
            "swap",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(f"{self.router_address}::curves::{self.pool_type}"))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_y_decimals,
            amount_y_decimals=amount_in_x_decimals
        )
