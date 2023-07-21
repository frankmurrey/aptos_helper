import random

from typing import Union

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import (Account,
                               AccountAddress)
from aptos_rest_client.client import ClientConfig

from loguru import logger

from modules.base import AptosBase
from contracts.tokens import Tokens

from src.schemas.thala import ThalaAddLiquidityConfigSchema, ThalaStakeConfigSchema

from modules.thala.math import Math, get_pair_amount_in


class Thala(AptosBase):
    base_pool_address = "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null"
    stable_scripts_address = "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool_scripts"
    scripts_address = "0x6b3720cd988adeaf721ed9d4730da4324d52364871a68eac62b46d21e4d2fa99::scripts"
    default_lp_stake_pool_id = 7

    def __init__(self,
                 config: Union[ThalaAddLiquidityConfigSchema, ThalaStakeConfigSchema],
                 base_url: str,
                 proxies: dict = None
                 ):
        super().__init__(base_url=base_url,
                         proxies=proxies)
        self.config = config
        self.coin_x = Tokens().get_by_name(name_query=config.coin_x)
        self.coin_y = Tokens().get_by_name(name_query=config.coin_y)

        self.pools_data = self.get_pools_data()

        self.amount_out_x_decimals = None
        self.amount_out_y_decimals = None

    def get_liquidity_pool_data(self,
                                coin_x,
                                coin_y,
                                base_pool_x,
                                base_pool_y,):
        response_url = "https://app.thala.fi/api/liquidity-pool"
        payload = {
            "pool-type": f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePool"
                         f"<{coin_x.contract}, {coin_y.contract}, {base_pool_x}, {base_pool_y}>"
        }
        response = self.client.get(url=response_url,
                                   params=payload)
        if not response.json():
            return None

        return response.json()

    def get_wallet_lp_balance(self,
                              account_address: AccountAddress,
                              lp_address: str):
        wallet_lp_resource = self.account_resource(
            account_address,
            f"0x1::coin::CoinStore<{lp_address}>"
        )
        wallet_lp_balance = wallet_lp_resource["data"]["coin"]["value"]

        return wallet_lp_balance

    def get_staked_lp_amount(self,
                             wallet_address: AccountAddress,
                             pool_id: int = None):
        if not pool_id:
            pool_id = self.default_lp_stake_pool_id

        response_url = f"{self.base_url}view"
        payload = {
            "function": "0x6b3720cd988adeaf721ed9d4730da4324d52364871a68eac62b46d21e4d2fa99"
                        "::farming::stake_and_reward_amount",
            "arguments": [
                str(wallet_address),
                str(pool_id)
            ],
            "type_arguments": [
                "0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL"
            ]
        }
        response = self.client.post(url=response_url,
                                    json=payload)

        if response.status_code != 200:
            return None

        return response.json()

    def get_lp_ratio(self,
                     coin_x,
                     coin_y,
                     base_pool_x,
                     base_pool_y,
                     account_address: AccountAddress):

        lp_addr = f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePoolToken" \
                  f"<{coin_x.contract}, {coin_y.contract}, {base_pool_x}, {base_pool_y}>"
        token_info = self.account_resource(
            AccountAddress.from_hex("0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af"),
            f"0x1::coin::CoinInfo<{lp_addr}>"
        )
        lp_supply = token_info.get("data").get("supply").get("vec")[0].get("integer").get("vec")[0].get("value")

        wallet_lp_balance = self.get_wallet_lp_balance(account_address,
                                                       lp_addr)

        lp_ratio = Math.fraction(int(wallet_lp_balance) // 100,
                                 int(lp_supply))

        return lp_ratio

    def get_pools_data(self) -> Union[dict, None]:
        request_url = "https://app.thala.fi/api/liquidity-pools"
        response = self.client.get(url=request_url)
        if response.status_code > 304 or not response.json():
            return None

        return response.json()

    def get_pool_for_token_pair(self):
        pools_data = self.pools_data.get('data')
        if not pools_data:
            return

        try:
            all_pool_types = []
            for pool in pools_data:
                pool_type = pool.get('poolType')
                if "stable_pool" not in pool_type:
                    continue
                split_pool_type = pool_type.split('<')[1]
                split_pool_type = split_pool_type.split('>')[0]
                split_pool_type = split_pool_type.split(', ')
                if len(split_pool_type) != 4:
                    continue

                all_pool_types.append(split_pool_type)

            for pool_type in all_pool_types:
                double_pool_type = f"{pool_type[0]}, {pool_type[1]}"
                if self.coin_x.contract in double_pool_type and self.coin_y.contract in double_pool_type:
                    coin_x, coin_y, _, _ = pool_type
                    return pool_type
        except Exception as e:
            logger.error(f"Error while getting pool for token pair: {e}")

        return None

    def get_amount_out_for_token_pair(self, wallet_address: AccountAddress):
        pool_data = self.get_pool_for_token_pair()
        if pool_data is None:
            base_pool_address_x = self.base_pool_address
            base_pool_address_y = self.base_pool_address
        else:
            self.coin_x = Tokens().get_by_contract(pool_data[0])
            self.coin_y = Tokens().get_by_contract(pool_data[1])
            base_pool_address_x = pool_data[2]
            base_pool_address_y = pool_data[3]

        wallet_x_balance = self.get_wallet_token_balance(wallet_address=wallet_address,
                                                         token_obj=self.coin_x)
        wallet_x_balance_decimals = self.get_amount_decimals(amount=wallet_x_balance,
                                                             token_obj=self.coin_x)
        wallet_y_balance = self.get_wallet_token_balance(wallet_address=wallet_address,
                                                         token_obj=self.coin_y)
        wallet_y_balance_decimals = self.get_amount_decimals(amount=wallet_y_balance,
                                                             token_obj=self.coin_y)

        if wallet_x_balance == 0 or wallet_y_balance == 0:
            logger.error(f"Wallet token balance should be > 0,"
                         f" ({wallet_x_balance_decimals} {self.coin_x.symbol.upper()},"
                         f" {wallet_y_balance_decimals} {self.coin_y.symbol.upper()})")
            return

        if wallet_x_balance_decimals < self.config.max_amount_out or wallet_y_balance_decimals < self.config.max_amount_out:
            min_balance = min(wallet_x_balance_decimals, wallet_y_balance_decimals)
            amount_out_decimals = random.uniform(self.config.min_amount_out, min_balance)
        else:
            amount_out_decimals = random.uniform(self.config.min_amount_out, self.config.max_amount_out)

        if self.config.send_all_balance is True:
            amount_out_x = wallet_x_balance
            amount_out_y = wallet_y_balance
            self.amount_out_x_decimals = wallet_x_balance_decimals
            self.amount_out_y_decimals = wallet_y_balance_decimals
        else:
            amount_out_x = int(amount_out_decimals * 10 ** self.get_token_decimals(token_obj=self.coin_x))
            amount_out_y = int(amount_out_decimals * 10 ** self.get_token_decimals(token_obj=self.coin_y))
            self.amount_out_x_decimals = round(amount_out_decimals, 4)
            self.amount_out_y_decimals = round(amount_out_decimals, 4)

        return {self.coin_x.contract: amount_out_x,
                self.coin_y.contract: amount_out_y,
                "base_pool_address_x": base_pool_address_x,
                "base_pool_address_y": base_pool_address_y}

    def build_add_liquidity_transaction_payload(self, sender_account: Account):
        pair_data = self.get_amount_out_for_token_pair(wallet_address=sender_account.address())
        if pair_data is None:
            logger.error(f"Error getting amount out for token pair: "
                         f"{self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}")
            return
        try:
            amount_out_x = pair_data.get(self.coin_x.contract)
            amount_out_y = pair_data.get(self.coin_y.contract)
            base_pool_address_x = pair_data.get("base_pool_address_x")
            base_pool_address_y = pair_data.get("base_pool_address_y")

            transaction_args = [
                TransactionArgument(int(amount_out_x), Serializer.u64),
                TransactionArgument(int(amount_out_y), Serializer.u64),
                TransactionArgument(0, Serializer.u64),
                TransactionArgument(0, Serializer.u64),

            ]

            payload = EntryFunction.natural(
                f"{self.stable_scripts_address}",
                "add_liquidity",
                [TypeTag(StructTag.from_str(self.coin_x.contract)),
                 TypeTag(StructTag.from_str(self.coin_y.contract)),
                 TypeTag(StructTag.from_str(base_pool_address_x)),
                 TypeTag(StructTag.from_str(base_pool_address_y))],
                transaction_args
            )

            return payload

        except Exception as e:
            logger.error(f"Error while building transaction payload: {e}")
            return None

    def send_add_liquidity_transaction(self, private_key: str):

        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_add_liquidity_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            logger.error(f"Error building add liquidity transaction payload")
            return False

        raw_transaction = self.build_raw_transaction(
            sender_account=sender_account,
            payload=txn_payload,
            gas_limit=int(self.config.gas_limit),
            gas_price=int(self.config.gas_price)
        )
        ClientConfig.max_gas_amount = int(self.config.gas_limit * 1.2)

        simulate_txn = self.estimate_transaction(raw_transaction=raw_transaction,
                                                 sender_account=sender_account)

        txn_info_message = f"Add liquidity: {self.amount_out_x_decimals} {self.coin_x.symbol.upper()}/" \
                           f"{self.amount_out_y_decimals} {self.coin_y.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message
        )

        return txn_status

    def get_amount_in_x_y(self, sender_account: Account,
                          pool_data):
        self.coin_x = Tokens().get_by_contract(pool_data[0])
        self.coin_y = Tokens().get_by_contract(pool_data[1])
        base_pool_address_x = pool_data[2]
        base_pool_address_y = pool_data[3]

        lp_ratio = self.get_lp_ratio(
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            base_pool_x=base_pool_address_x,
            base_pool_y=base_pool_address_y,
            account_address=sender_account.address()
        )
        if lp_ratio is None:
            logger.error(f"Error getting lp ratio")
            return

        liquidity_pool_data = self.get_liquidity_pool_data(
            coin_x=self.coin_x,
            coin_y=self.coin_y,
            base_pool_x=base_pool_address_x,
            base_pool_y=base_pool_address_y,
        )
        if liquidity_pool_data is None:
            logger.error(f"Error getting liquidity pool data")
            return

        lp_balance = liquidity_pool_data.get("data").get("balances")
        if len(lp_balance) < 2:
            logger.error(f"Error getting lp balance")
            return

        lp_balance_x = float(lp_balance[0]) * 10 ** 6
        lp_balance_y = float(lp_balance[1]) * 10 ** 6

        amount_in_x, amount_in_y = get_pair_amount_in(
            lp_balance_x=int(lp_balance_x),
            lp_balance_y=int(lp_balance_y),
            lp_ratio=lp_ratio
        )

        if amount_in_x is None or amount_in_y is None:
            logger.error(f"Error getting amount in")
            return

        return {self.coin_x.contract: amount_in_x,
                self.coin_y.contract: amount_in_y}

    def build_remove_liquidity_transaction_payload(self, sender_account: Account):
        pool_data = self.get_pool_for_token_pair()
        if pool_data is None:
            logger.error(f"Error getting pool data")
            return None

        self.coin_x = Tokens().get_by_contract(pool_data[0])
        self.coin_y = Tokens().get_by_contract(pool_data[1])
        base_pool_address_x = pool_data[2]
        base_pool_address_y = pool_data[3]

        lp_addr = f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePoolToken" \
                  f"<{self.coin_x.contract}, {self.coin_y.contract}, {base_pool_address_x}, {base_pool_address_y}>"
        wallet_lp_balance = self.get_wallet_lp_balance(
            account_address=sender_account.address(),
            lp_address=lp_addr
        )

        if wallet_lp_balance is None:
            logger.error(f"Error getting wallet lp balance")
            return None

        if float(wallet_lp_balance) == 0:
            logger.error(f"Wallet lp balance is 0, nothing to remove")
            return None

        amount_in_x_y = self.get_amount_in_x_y(
            sender_account=sender_account,
            pool_data=pool_data
        )
        if amount_in_x_y is None:
            logger.error(f"Error getting amount in")
            return None

        amount_in_x = amount_in_x_y.get(self.coin_x.contract)
        amount_in_y = amount_in_x_y.get(self.coin_y.contract)
        if amount_in_x is None or amount_in_y is None:
            logger.error(f"Error getting amount in")
            return None

        transaction_args = [
            TransactionArgument(int(wallet_lp_balance), Serializer.u64),
            TransactionArgument(int(amount_in_x), Serializer.u64),
            TransactionArgument(int(amount_in_y), Serializer.u64),
            TransactionArgument(0, Serializer.u64),
            TransactionArgument(0, Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.stable_scripts_address}",
            "remove_liquidity",
            [TypeTag(StructTag.from_str(self.coin_x.contract)),
             TypeTag(StructTag.from_str(self.coin_y.contract)),
             TypeTag(StructTag.from_str(base_pool_address_x)),
             TypeTag(StructTag.from_str(base_pool_address_y))],
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

        txn_info_message = f"Remove liquidity of pair: {self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message
        )

        return txn_status

    def build_stake_lp_transaction_payload(self,
                                           sender_account: Account,
                                           pool_id = None):
        pool_data = self.get_pool_for_token_pair()
        if pool_data is None:
            logger.error(f"Error getting pool data")
            return None

        self.coin_x = Tokens().get_by_contract(pool_data[0])
        self.coin_y = Tokens().get_by_contract(pool_data[1])
        base_pool_address_x = pool_data[2]
        base_pool_address_y = pool_data[3]

        lp_addr = f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePoolToken" \
                  f"<{self.coin_x.contract}, {self.coin_y.contract}, {base_pool_address_x}, {base_pool_address_y}>"
        print(lp_addr)
        wallet_lp_balance = self.get_wallet_lp_balance(
            account_address=sender_account.address(),
            lp_address=lp_addr
        )

        if wallet_lp_balance is None:
            logger.error(f"Error getting wallet lp balance")
            return None

        if float(wallet_lp_balance) == 0:
            logger.error(f"Wallet lp balance is 0, nothing to stake")
            return None

        if pool_id is None:
            pool_id = self.default_lp_stake_pool_id

        transaction_args = [
            TransactionArgument(int(pool_id), Serializer.u64),
            TransactionArgument(int(wallet_lp_balance), Serializer.u64),
        ]
        split_lp_addr = lp_addr.split("::")
        name = "".join(lp_addr.split("stable_pool::")[1])
        payload = EntryFunction.natural(
            f"{self.scripts_address}",
            "stake",
            [TypeTag(StructTag(address=AccountAddress.from_hex(split_lp_addr[0]),
                               module=split_lp_addr[1],
                               name=name,
                               type_args=[]))],
            transaction_args
        )

        return payload

    def send_stake_lp_transaction(self,
                                  private_key: str):
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_stake_lp_transaction_payload(sender_account=sender_account,
                                                              pool_id=self.default_lp_stake_pool_id)

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

        txn_info_message = f"LP stake of pair: {self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            simulation_status=simulate_txn,
            txn_info_message=txn_info_message
        )

        return txn_status
