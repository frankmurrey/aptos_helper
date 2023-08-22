import random
import time

from typing import Union
from math import pow

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import Account
from loguru import logger

from modules.base import AptosBase
from modules.liquidity_swap.math import (get_coins_out_with_fees_stable,
                                         get_coins_out_with_fees,
                                         d)

from contracts.tokens import Tokens

from src.schemas.liquidity_swap import LiqSwSwapConfigSchema

from src.utils.token_price_alert import TokenPriceAlert
from src.utils.coingecko_pricer import GeckoPricer


class Swap(AptosBase):
    token: Tokens
    config: LiqSwSwapConfigSchema
    base_url: str

    def __init__(self, config: LiqSwSwapConfigSchema, base_url: str, proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.token = Tokens()
        self.config = config

        self.gecko_pricer = GeckoPricer(proxies=self.proxies)

        self.coin_to_swap = self.token.get_by_name(name_query=self.config.coin_to_swap)
        self.coin_to_receive = self.token.get_by_name(name_query=self.config.coin_to_receive)

        self.resource_data = None

        self.amount_out_decimals = None
        self.amount_in_decimals = None
        self.pool_type = None

        self.liq_swap_address = self.get_address_from_hex(
                "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12")

    def get_token_pair_reserve(self,
                               pool_type: str) -> Union[dict, None]:
        coin_x = self.coin_to_swap.contract
        coin_y = self.coin_to_receive.contract

        resource_acc_address = self.get_address_from_hex(
            "0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948")
        res_payload = f"{self.liq_swap_address}::liquidity_pool::LiquidityPool" \
                      f"<{coin_x}, {coin_y}, {self.liq_swap_address}::curves::{pool_type}>"
        resource_data = self.get_token_reserve(resource_address=resource_acc_address,
                                               payload=res_payload)

        if resource_data is False:
            logger.error(f"Error getting token pair reserve, {pool_type} pool")
            return None

        if resource_data is not None:
            self.resource_data = resource_data

            reserve_x = resource_data["data"]["coin_x_reserve"]["value"]
            reserve_y = resource_data["data"]["coin_y_reserve"]["value"]

            return {coin_x: reserve_x, coin_y: reserve_y}
        else:
            coin_x = self.coin_to_swap.contract
            coin_y = self.coin_to_receive.contract

            res_payload = f"{self.liq_swap_address}::liquidity_pool::LiquidityPool" \
                          f"<{coin_y}, {coin_x}, {self.liq_swap_address}::curves::{pool_type}>"

            reversed_data = self.get_token_reserve(resource_address=resource_acc_address,
                                                   payload=res_payload)
            if reversed_data is False:
                logger.error(f"Error getting token pair reserve, {pool_type} pool")
                return None

            self.resource_data = reversed_data
            reserve_x = reversed_data["data"]["coin_x_reserve"]["value"]
            reserve_y = reversed_data["data"]["coin_y_reserve"]["value"]

            return {coin_x: reserve_y, coin_y: reserve_x}

    def get_amount_in_stable_pool(self,
                                  amount_out: int):
        tokens_reserve: dict = self.get_token_pair_reserve(pool_type="Stable")
        if tokens_reserve is None:
            return None

        reserve_x = int(tokens_reserve[self.coin_to_swap.contract])
        reserve_y = int(tokens_reserve[self.coin_to_receive.contract])

        if reserve_x is None or reserve_y is None:
            return None

        pool_fee = int(self.resource_data["data"]["fee"])

        amount_in = get_coins_out_with_fees_stable(
            coin_in=d(amount_out),
            reserve_in=d(reserve_x),
            reserve_out=d(reserve_y),
            scale_in=d(pow(10, self.get_token_decimals(token_obj=self.coin_to_swap))),
            scale_out=d(pow(10, self.get_token_decimals(token_obj=self.coin_to_receive))),
            fee=d(pool_fee)
        )

        return amount_in

    def get_amount_in_uncorrelated_pool(self,
                                        amount_out: int):
        tokens_reserve: dict = self.get_token_pair_reserve(pool_type="Uncorrelated")

        if tokens_reserve is None:
            return None

        reserve_x = int(tokens_reserve[self.coin_to_swap.contract])
        reserve_y = int(tokens_reserve[self.coin_to_receive.contract])

        if reserve_x is None or reserve_y is None:
            return None

        pool_fee = int(self.resource_data["data"]["fee"])

        amount_in = get_coins_out_with_fees(coin_in_val=d(amount_out),
                                            reserve_in=d(reserve_x),
                                            reserve_out=d(reserve_y),
                                            fee=d(pool_fee))

        return amount_in

    def get_most_profitable_amount_in_and_set_pool_type(self, amount_out: int):
        stable_pool_amount_in = self.get_amount_in_stable_pool(amount_out=amount_out)
        token_decimals = self.get_token_decimals(token_obj=self.coin_to_receive)

        if stable_pool_amount_in is None:
            return None

        uncorrelated_pool_amount_in = self.get_amount_in_uncorrelated_pool(amount_out=amount_out)

        if uncorrelated_pool_amount_in is None:
            return None

        if stable_pool_amount_in > uncorrelated_pool_amount_in:
            self.pool_type = "Stable"
            self.amount_in_decimals = stable_pool_amount_in / 10 ** token_decimals
            return stable_pool_amount_in

        self.pool_type = "Uncorrelated"
        self.amount_in_decimals = uncorrelated_pool_amount_in / 10 ** token_decimals
        return uncorrelated_pool_amount_in

    def get_amount_out(self, wallet_address):
        wallet_token_balance = self.get_wallet_token_balance(wallet_address=wallet_address,
                                                             token_obj=self.coin_to_swap)

        if wallet_token_balance == 0:
            logger.error(f"Wallet balance is 0 {self.coin_to_swap.symbol.upper()}")
            return None

        wallet_token_balance_decimals = wallet_token_balance * 10 ** self.get_token_decimals(
            token_obj=self.coin_to_swap)

        if self.config.send_all_balance is True:
            amount_out = wallet_token_balance

        elif self.config.send_percent_balance is True:
            percent = random.randint(self.config.min_amount_out, self.config.max_amount_out) / 100
            amount_out = int(wallet_token_balance * percent)

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=wallet_token_balance_decimals,
                decimals=self.get_token_decimals(token_obj=self.coin_to_swap)
            )

        else:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=self.get_token_decimals(token_obj=self.coin_to_swap)
            )

        self.amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                            token_obj=self.coin_to_swap)

        is_wallet_valid_for_swap = self.check_account_balance_before_transaction(amount_out=amount_out,
                                                                                 wallet_address=wallet_address,
                                                                                 token_obj=self.coin_to_swap)
        if is_wallet_valid_for_swap is False:
            return None

        return amount_out

    def check_if_price_valid_for_swap(self):
        if self.coin_to_swap.gecko_id is None or self.coin_to_receive.gecko_id is None:
            logger.error("Gecko id not found for coin pair, please provide manually in contracts/tokens.json")
            return None

        target_price = float(self.amount_in_decimals) / float(self.amount_out_decimals)
        token_pair_price = self.gecko_pricer.get_simple_price_of_token_pair(x_token_id=self.coin_to_swap.gecko_id,
                                                                            y_token_id=self.coin_to_receive.gecko_id)
        if token_pair_price is None:
            logger.error("Error getting actual token pair price")
            return None

        actual_price = token_pair_price[self.coin_to_swap.gecko_id] / token_pair_price[
            self.coin_to_receive.gecko_id]
        is_price_valid = TokenPriceAlert.is_target_price_valid(target_price=target_price,
                                                               actual_gecko_price=actual_price,
                                                               max_price_difference_percent=self.config.max_price_difference)
        if is_price_valid is False:
            logger.error(f"Price is not valid for "
                         f"{self.coin_to_swap.gecko_id.upper()}/{self.coin_to_receive.gecko_id.upper()}, "
                         f"actual CoinGecko price ({round(actual_price, 5)}) "
                         f"is better than execution price ({round(target_price, 5)})")
            return None

        logger.info(f"Price is valid for swap (source: CoinGecko)")
        return True

    def build_transaction_payload(self, sender_account: Account):
        amount_out = self.get_amount_out(wallet_address=sender_account.address())
        amount_in = self.get_most_profitable_amount_in_and_set_pool_type(amount_out=amount_out)

        if amount_in is None or amount_out is None:
            return None

        if self.config.compare_with_actual_price is True:
            is_price_valid = self.check_if_price_valid_for_swap()
            if is_price_valid is None:
                return None

        transaction_args = [
            TransactionArgument(int(amount_out), Serializer.u64),
            TransactionArgument(int(amount_in), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.liq_swap_address}::scripts_v2",
            "swap",
            [TypeTag(StructTag.from_str(self.coin_to_swap.contract)),
             TypeTag(StructTag.from_str(self.coin_to_receive.contract)),
             TypeTag(StructTag.from_str(f"{self.liq_swap_address}::curves::{self.pool_type}"))],
            transaction_args
        )

        return payload

    def make_swap(self, private_key: str) -> bool:
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        txn_info_message = f"Swap (Liquid Swap, {self.pool_type} pool) {self.amount_out_decimals} ({self.coin_to_swap.name}) ->" \
                           f" {self.amount_in_decimals} ({self.coin_to_receive.name})."

        is_token_registered_by_wallet = self.is_token_registered_for_address(wallet_address=sender_account.address(),
                                                                             token_contract=self.coin_to_receive.contract)

        if is_token_registered_by_wallet is False:
            logger.warning(f"Coin {self.coin_to_receive.symbol.upper()} is not registered on address")
            reg_status = self.register_coin_for_wallet(sender_account=sender_account,
                                                       token_obj=self.coin_to_receive,
                                                       config=self.config)
            if reg_status is False:
                return False

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        txn_status, txn_status_message = txn_status

        incorrect_output_error = 'ERR_COIN_OUT_NUM_LESS_THAN_EXPECTED_MINIMUM'
        if incorrect_output_error in txn_status_message:
            logger.warning(f"Price updated, retrying swap (after 3 sec) with fresh amount out")
            time.sleep(3)

            updated_payload = self.build_transaction_payload(sender_account=sender_account)
            if updated_payload is None:
                return False

            txn_info_message = f"Swap (Liquid Swap, {self.pool_type} pool) {self.amount_out_decimals} ({self.coin_to_swap.name}) ->" \
                               f" {self.amount_in_decimals} ({self.coin_to_receive.name})."

            txn_status = self.simulate_and_send_transfer_type_transaction(
                config=self.config,
                sender_account=sender_account,
                txn_payload=updated_payload,
                txn_info_message=txn_info_message
            )
            txn_status, txn_status_message = txn_status

        return txn_status
