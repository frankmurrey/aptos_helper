from typing import Union

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import Account
from aptos_rest_client.client import ClientConfig


from loguru import logger

from modules.base import AptosBase
from contracts.tokens import Tokens

from modules.liquidity_swap.math import (get_coins_out_with_fees_stable,
                                         get_optimal_liquidity_amount,
                                         d)

from src.schemas.liquidity_swap import LiqSwAddLiquidityConfigSchema


class Liquidity(AptosBase):
    tokens: Tokens
    config: LiqSwAddLiquidityConfigSchema
    base_url: str

    def __init__(self, config, base_url: str, proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.tokens = Tokens()
        self.config = config

        self.coin_x = self.tokens.get_by_name(name_query=self.config.coin_x)
        self.coin_y = self.tokens.get_by_name(name_query=self.config.coin_y)

        self.resource_data = None

        self.amount_out_x_decimals = None
        self.amount_out_y_decimals = None

        self.liq_swap_address = self.get_address_from_hex(
            "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12")

    def get_staked_pair_balance(self,
                               wallet_address):
        url = "https://sentrio-api.pontem.network/api/liq"
        payload = {
            "address": wallet_address,
            "x": self.coin_x.contract,
            "y": self.coin_y.contract,
            "curve": f"{self.liq_swap_address}::curves::Stable"
        }
        response = self.client.get(url=url, params=payload)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_token_pair_reserve(self) -> Union[dict, None]:
        resource_acc_address = self.get_address_from_hex(
            "0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948")
        res_payload = f"{self.liq_swap_address}::liquidity_pool::LiquidityPool" \
                      f"<{self.coin_x.contract}, {self.coin_y.contract}, {self.liq_swap_address}::curves::Stable>"

        resource_data = self.get_token_reserve(resource_address=resource_acc_address,
                                               payload=res_payload)

        if resource_data is False:
            logger.error("Error getting token pair reserve")
            return None

        if resource_data is not None:
            self.resource_data = resource_data

            reserve_x = resource_data["data"]["coin_x_reserve"]["value"]
            reserve_y = resource_data["data"]["coin_y_reserve"]["value"]

            return {self.coin_x.contract: reserve_x,
                    self.coin_y.contract: reserve_y}
        else:
            logger.error(f"({self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}) pool does not exist. "
                         f"Try reverse pool ({self.coin_y.symbol.upper()}-{self.coin_x.symbol.upper()}).")
            return None

    def get_amount_y_out(self,
                         amount_out: int,
                         tokens_reserve):
        reserve_x = int(tokens_reserve[self.coin_x.contract])
        reserve_y = int(tokens_reserve[self.coin_y.contract])

        if reserve_x is None or reserve_y is None:
            return None

        amount_in = get_optimal_liquidity_amount(
            x_desired=d(amount_out),
            x_reserve=d(reserve_x),
            y_reserve=d(reserve_y)
        )

        return amount_in

    def build_add_liquidity_transaction_payload(self, sender_account: Account,):
        tokens_reserve: dict = self.get_token_pair_reserve()
        if tokens_reserve is None:
            return None

        wallet_token_balance_x = self.get_wallet_token_balance(wallet_address=sender_account.address(),
                                                               token_obj=self.coin_x)
        wallet_token_balance_y = self.get_wallet_token_balance(wallet_address=sender_account.address(),
                                                               token_obj=self.coin_y)
        if wallet_token_balance_x is None or wallet_token_balance_y is None:
            logger.error("Error getting wallet token balance")
            return None

        if wallet_token_balance_x == 0 or wallet_token_balance_y == 0:
            logger.error(f"Wallet token balance is 0: "
                         f"{wallet_token_balance_x} {self.coin_x.symbol.upper}, "
                         f"{wallet_token_balance_y} {self.coin_y.symbol.upper}")
            return None

        wallet_token_balance_decimals_x = wallet_token_balance_x / 10 ** self.get_token_decimals(
            token_obj=self.coin_x)
        wallet_token_balance_decimals_y = wallet_token_balance_y / 10 ** self.get_token_decimals(
            token_obj=self.coin_y)

        if self.config.send_all_balance:
            amount_out_x = wallet_token_balance_x

        elif wallet_token_balance_decimals_x < self.config.max_amount_out:
            amount_out_x = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=wallet_token_balance_decimals_x,
                decimals=self.get_token_decimals(token_obj=self.coin_x)
            )
        else:
            amount_out_x = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=self.get_token_decimals(token_obj=self.coin_x)
            )

        amount_out_x_slippage = amount_out_x - (amount_out_x * self.config.slippage / 100)
        amount_out_y = self.get_amount_y_out(amount_out=amount_out_x,
                                             tokens_reserve=tokens_reserve)
        if amount_out_y is None:
            logger.error("Error getting amount out")
            return None

        if amount_out_y == 0:
            logger.error("Amount out is 0")
            return None

        amount_out_y_slippage = int(amount_out_y) - (int(amount_out_y) * self.config.slippage / 100)

        amount_out_y_decimals = amount_out_y / 10 ** self.get_token_decimals(token_obj=self.coin_y)
        if amount_out_y > wallet_token_balance_y:
            logger.error(f"Amount out Y is greater than wallet token balance: "
                         f"need: {amount_out_y_decimals} {self.coin_y.symbol.upper()}, "
                         f"balance: {wallet_token_balance_decimals_y} {self.coin_y.symbol.upper()}")
            return None

        self.amount_out_x_decimals = amount_out_x / 10 ** self.get_token_decimals(token_obj=self.coin_x)
        self.amount_out_y_decimals = amount_out_y_decimals

        transaction_args = [
            TransactionArgument(int(amount_out_x), Serializer.u64),
            TransactionArgument(int(amount_out_x_slippage), Serializer.u64),
            TransactionArgument(int(amount_out_y), Serializer.u64),
            TransactionArgument(int(amount_out_y_slippage), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.liq_swap_address}::scripts_v2",
            "add_liquidity",
            [TypeTag(StructTag.from_str(self.coin_x.contract)),
             TypeTag(StructTag.from_str(self.coin_y.contract)),
             TypeTag(StructTag.from_str(f"{self.liq_swap_address}::curves::Stable"))],
            transaction_args
        )

        return payload

    def send_add_liquidity_transaction(self, private_key: str):
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_add_liquidity_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        raw_transaction = self.build_raw_transaction(
            sender_account=sender_account,
            payload=txn_payload,
            gas_limit=int(self.config.gas_limit),
            gas_price=int(self.config.gas_price)
        )
        ClientConfig.max_gas_amount = int(self.config.gas_limit)

        simulate_txn = self.estimate_transaction(raw_transaction=raw_transaction,
                                                 sender_account=sender_account)

        txn_info_message = (
            f"Add liquidity (Liquid Swap) - " 
            f"{round(self.amount_out_x_decimals, 4)} ({self.coin_x.name}) + " 
            f"{round(self.amount_out_y_decimals, 4)} ({self.coin_y.name})."
        )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message)

        return txn_status

    def build_remove_liquidity_transaction_payload(self, sender_account: Account):
        is_tokens_reserve_exists = self.get_token_pair_reserve()
        if not is_tokens_reserve_exists:
            return None

        lp_addr = f"0x5a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948::lp_coin::LP" \
                  f"<{self.coin_x.contract}, {self.coin_y.contract}, {self.liq_swap_address}::curves::Stable>"
        wallet_lp_balance = self.get_wallet_token_balance(token_contract=lp_addr,
                                                          wallet_address=sender_account.address())

        if wallet_lp_balance == 0:
            logger.error(f"Wallet ({self.coin_x.symbol.upper()}-{self.coin_y.symbol.upper()}) lp coin balance is 0")
            return None

        staked_pair_balance = self.get_staked_pair_balance(wallet_address=sender_account.address())
        if not staked_pair_balance:
            logger.error(f"Error while fetching staked pair amounts")

        balance_x = int(staked_pair_balance['x'])
        balance_y = int(staked_pair_balance['y'])

        min_amount_in_x = balance_x - (balance_x * self.config.slippage / 100)
        min_amount_in_y = balance_y - (balance_y * self.config.slippage / 100)

        self.amount_out_x_decimals = min_amount_in_x / 10 ** self.get_token_decimals(token_obj=self.coin_x)
        self.amount_out_y_decimals = min_amount_in_y / 10 ** self.get_token_decimals(token_obj=self.coin_y)

        transaction_args = [
            TransactionArgument(int(wallet_lp_balance), Serializer.u64),
            TransactionArgument(int(min_amount_in_x), Serializer.u64),
            TransactionArgument(int(min_amount_in_y), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.liq_swap_address}::scripts_v2",
            "remove_liquidity",
            [TypeTag(StructTag.from_str(self.coin_x.contract)),
             TypeTag(StructTag.from_str(self.coin_y.contract)),
             TypeTag(StructTag.from_str(f"{self.liq_swap_address}::curves::Stable"))],
            transaction_args
        )

        return payload

    def send_remove_liquidity_transaction(self, private_key: str):
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_remove_liquidity_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        raw_transaction = self.build_raw_transaction(
            sender_account=sender_account,
            payload=txn_payload,
            gas_limit=int(self.config.gas_limit),
            gas_price=int(self.config.gas_price)
        )
        ClientConfig.max_gas_amount = int(self.config.gas_limit)

        simulate_txn = self.estimate_transaction(raw_transaction=raw_transaction,
                                                 sender_account=sender_account)

        txn_info_message = f"Remove liquidity (Liquidity Swap): " \
                           f"({round(self.amount_out_x_decimals, 4)} {self.coin_x.symbol.upper()} / " \
                           f"{round(self.amount_out_y_decimals, 4)} {self.coin_y.symbol.upper()})"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message
        )

        return txn_status

