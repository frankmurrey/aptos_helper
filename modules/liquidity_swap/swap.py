from typing import Union

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import Account
from aptos_rest_client.client import (ResourceNotFound,
                                      ClientConfig)

from loguru import logger

from modules.base import AptosBase

from contracts.tokens import Tokens

from src.schemas.liquidity_swap import LiqSwSwapConfigSchema


class Swap(AptosBase):
    token: Tokens
    config: LiqSwSwapConfigSchema
    base_url: str

    def __init__(self, config: LiqSwSwapConfigSchema, base_url: str, proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.token = Tokens()
        self.config = config

        self.coin_to_swap = self.token.get_by_name(name_query=self.config.coin_to_swap)
        self.coin_to_receive = self.token.get_by_name(name_query=self.config.coin_to_receive)

        self.amount_out_decimals = None
        self.amount_in_decimals = None

        self.liq_swap_address = self.get_address_from_hex(
                "0x190d44266241744264b964a37b8f09863167a12d3e70cda39376cfb4e3561e12")

    def get_token_pair_reserve(self) -> Union[dict, None]:
        coin_x = self.coin_to_swap.contract
        coin_y = self.coin_to_receive.contract

        resource_acc_address = self.get_address_from_hex(
            "0x05a97986a9d031c4567e15b797be516910cfcb4156312482efc6a19c0a30c948")
        res_payload = f"{self.liq_swap_address}::liquidity_pool::LiquidityPool" \
                      f"<{coin_x}, {coin_y}, {self.liq_swap_address}::curves::Stable>"

        resource_data = self.get_token_reserve(coin_x=coin_x,
                                               coin_y=coin_y,
                                               resource_address=resource_acc_address,
                                               payload=res_payload)

        if resource_data is False:
            logger.error("Error getting token pair reserve")
            return None

        if resource_data is not None:
            reserve_x = resource_data["data"]["coin_x_reserve"]["value"]
            reserve_y = resource_data["data"]["coin_y_reserve"]["value"]

            return {coin_x: reserve_x, coin_y: reserve_y}
        else:
            coin_x = self.coin_to_swap.contract
            coin_y = self.coin_to_receive.contract

            res_payload = f"{self.liq_swap_address}::liquidity_pool::LiquidityPool" \
                          f"<{coin_y}, {coin_x}, {self.liq_swap_address}::curves::Uncorrelated>"

            reversed_data = self.get_token_reserve(coin_x=coin_y,
                                                   coin_y=coin_x,
                                                   resource_address=resource_acc_address,
                                                   payload=res_payload)
            if reversed_data is False:
                logger.error("Error getting token pair reserve")
                return None

            reserve_x = reversed_data["data"]["coin_x_reserve"]["value"]
            reserve_y = reversed_data["data"]["coin_y_reserve"]["value"]

            return {coin_x: reserve_x, coin_y: reserve_y}

    def get_amount_in(self, amount_out: int):
        tokens_reserve: dict = self.get_token_pair_reserve()
        if tokens_reserve is None:
            return None

        reserve_x = tokens_reserve[self.coin_to_swap.contract]
        reserve_y = tokens_reserve[self.coin_to_receive.contract]

        if reserve_x is None or reserve_y is None:
            return None

        amount_in_with_fee = amount_out * 9975

        numerator = amount_in_with_fee * int(reserve_y)
        denominator = int(reserve_x) * 10000 + amount_in_with_fee

        amount_in = numerator // denominator

        return amount_in

    def build_transaction_payload(self, sender_account: Account):
        wallet_token_balance = self.get_wallet_token_balance(wallet_address=sender_account.address(),
                                                             token_obj=self.coin_to_swap)
        if wallet_token_balance == 0:
            logger.error(f"Wallet balance is 0 {self.coin_to_swap.symbol}")
            return None

        wallet_token_balance_decimals = wallet_token_balance * 10 ** self.get_token_decimals(
            token_obj=self.coin_to_swap)

        if self.config.send_all_balance is True:
            amount_out = wallet_token_balance

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

        slippage = self.config.slippage
        amount_in = int(self.get_amount_in(amount_out=amount_out) * (1 - (slippage / 100)))

        if amount_in is None:
            return None

        self.amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                            token_obj=self.coin_to_swap)
        self.amount_in_decimals = self.get_amount_decimals(amount=amount_in,
                                                           token_obj=self.coin_to_receive)

        wallet_valid_for_swap = self.check_account_balance_before_transaction(amount_out=amount_out,
                                                                              wallet_address=sender_account.address(),
                                                                              token_obj=self.coin_to_swap)
        if wallet_valid_for_swap is False:
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
             TypeTag(StructTag.from_str(f"{self.liq_swap_address}::curves::Uncorrelated"))],
            transaction_args
        )

        return payload

    def make_swap(self, private_key: str) -> bool:

        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_transaction_payload(sender_account=sender_account)

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

        txn_info_message = f"Swap (Liquid Swap) {self.amount_out_decimals} ({self.coin_to_swap.name}) ->" \
                           f" {self.amount_in_decimals} ({self.coin_to_receive.name})."

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message)

        return txn_status

