import binascii

from modules.base import AptosBase

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)

from aptos_rest_client.client import ClientConfig

from contracts.tokens import Tokens
from contracts.chains import Chains

from src.schemas.aptos_bridge import AptosBridgeConfigSchema

from modules.the_aptos_bridge.src_lz.executor import Executor
from modules.the_aptos_bridge.src_lz.endpoint import Endpoint

from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import (Account,
                               AccountAddress)

from loguru import logger


class AptosBridge(AptosBase):
    def __init__(self,
                 config: AptosBridgeConfigSchema,
                 base_url: str,
                 proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.config = config
        self.bridge_address = self.get_address_from_hex(
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa"
        )
        self.amount_out_decimals = None

    def get_lz_fee(self,
                   dst_chain_id: int,
                   adapter_params):
        endpoint = Endpoint(self)

        fee = endpoint.quote_fee(
            ua_address=self.bridge_address,
            dst_chain_id=dst_chain_id,
            adapter_params=adapter_params,
            payload_size=74
        )
        return int(fee)

    def build_transaction_payload(self,
                                  sender_account: Account,
                                  receiver_address: str,):

        coin_to_bridge = Tokens().get_by_name(name_query=self.config.coin_to_bridge)
        dst_chain = Chains().get_by_name(name_query=self.config.dst_chain_name)
        dst_chain_id = dst_chain.id
        recipient_address = AccountAddress.from_hex(receiver_address)
        wallet_apt_balance = self.get_wallet_aptos_balance(wallet_address=sender_account.address())

        if wallet_apt_balance == 0:
            logger.error("Wallet Aptos balance is 0")
            return

        if not coin_to_bridge or not dst_chain:
            logger.error("Coin to bridge or destination chain not found")
            return

        executor = Executor(self)
        adapter_params = executor.get_default_adapter_params(dst_chain_id=dst_chain_id)

        fee = self.get_lz_fee(dst_chain_id=dst_chain_id,
                              adapter_params=adapter_params)
        if not fee:
            logger.error("Fee calculation failed")
            return

        if fee > int(wallet_apt_balance):
            logger.error("Not enough aptos balance for fee")
            return

        wallet_token_balance = self.get_wallet_token_balance(wallet_address=sender_account.address(),
                                                             token_obj=coin_to_bridge)

        if wallet_token_balance == 0:
            logger.error(f"Wallet token {coin_to_bridge.symbol} balance is 0")
            return

        wallet_token_balance_decimals = wallet_token_balance * 10 ** self.get_token_decimals(
            token_obj=coin_to_bridge)

        if self.config.send_all_balance:
            amount_out = wallet_token_balance

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=wallet_token_balance_decimals,
                decimals=self.get_token_decimals(token_obj=coin_to_bridge)
            )

        else:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=self.get_token_decimals(token_obj=coin_to_bridge)
            )

        self.amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                            token_obj=coin_to_bridge)

        is_wallet_balance_enough = self.check_account_balance_before_transaction(
            amount_out=amount_out,
            wallet_address=sender_account.address(),
            token_obj=coin_to_bridge
        )

        if not is_wallet_balance_enough:
            logger.error("Wallet balance is not enough for swap")
            return
        transaction_args = [
            TransactionArgument(int(dst_chain_id),
                                Serializer.u64),
            TransactionArgument(list(binascii.unhexlify(str(recipient_address)[2:])),
                                Serializer.sequence_serializer(Serializer.u8)),
            TransactionArgument(int(amount_out),
                                Serializer.u64),
            TransactionArgument(int(fee),
                                Serializer.u64),
            TransactionArgument(0,
                                Serializer.u64),
            TransactionArgument(False,
                                Serializer.bool),
            TransactionArgument(list(binascii.unhexlify(adapter_params[2:])),
                                Serializer.sequence_serializer(Serializer.u8)),
            TransactionArgument([],
                                Serializer.sequence_serializer(Serializer.u8)),
        ]

        payload = EntryFunction.natural(
            f"{self.bridge_address}::coin_bridge",
            "send_coin_from",
            [TypeTag(StructTag.from_str(coin_to_bridge.contract))],
            transaction_args
        )
        return payload

    def send_transaction(self,
                         private_key: str,
                         receiver_address: str):
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_transaction_payload(sender_account=sender_account,
                                                     receiver_address=receiver_address)

        if txn_payload is None:
            return False

        txn_info_message = f"{self.amount_out_decimals} {self.config.coin_to_bridge.upper()}" \
                           f" bridge to {self.config.dst_chain_name.upper()}, receiver: {receiver_address}."

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        return txn_status
