from typing import Union

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.account import (Account,
                               AccountAddress)
from aptos_rest_client.client import ResourceNotFound

from loguru import logger

from modules.base import AptosBase

from contracts.tokens import Tokens
from src.schemas.able_finance import (AbleMintConfigSchema,
                                      AbleRedeemConfigSchema)


class AbleFinance(AptosBase):
    store_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin::ACoinStore"
    lend_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin_lend"

    def __init__(self,
                 config: Union[AbleMintConfigSchema, AbleRedeemConfigSchema],
                 base_url: str,
                 proxies: dict = None):
        super().__init__(base_url=base_url,
                         proxies=proxies)
        self.config = config
        self.coin_option = Tokens().get_by_name(name_query=config.coin_option)

        self.amount_out_decimals = None

    def get_max_redeem_amount(self,
                              coin_contract: str,
                              account_address: AccountAddress):
        try:
            resource_type = f"{self.store_address}<{coin_contract}>"

            data = self.account_resource(
                account_address,
                resource_type
            )

            return data.get('data').get('coin').get('value')
        except ResourceNotFound:
            return None

    def build_redeem_transaction_payload(self, sender_account: Account):
        max_redeem_amount = self.get_max_redeem_amount(
            coin_contract=self.coin_option.contract,
            account_address=sender_account.address()
        )
        if max_redeem_amount is None:
            logger.error("LP not found on wallet balance")
            return

        if int(max_redeem_amount) == 0:
            logger.error("Nothing to redeem (claim)")
            return

        max_redeem_amount = int(max_redeem_amount)
        max_amount_out = int(self.config.max_amount_out) * 10 ** self.get_token_decimals(token_obj=self.coin_option)
        if max_amount_out > max_redeem_amount:
            logger.error(f"Max redeem amount: {max_redeem_amount}, trying to redeem: {self.config.max_amount_out}")
            return

        if self.config.redeem_all is True:
            amount_out = max_redeem_amount
        else:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=self.get_token_decimals(token_obj=self.coin_option)
            )

        self.amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                            token_obj=self.coin_option)

        transaction_args = [
            TransactionArgument(int(max_redeem_amount), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.lend_address}",
            "redeem_entry",
            [TypeTag(StructTag.from_str(self.coin_option.contract))],
            transaction_args
        )

        return payload

    def send_redeem_transaction(self, private_key: str) -> bool:
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_redeem_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        txn_info_message = f"Redeem/Claim (Abel finance) {self.amount_out_decimals} {self.coin_option.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        txn_status, txn_status_message = txn_status

        return txn_status

    def build_mint_transaction_payload(self, sender_account: Account):
        wallet_token_balance = self.get_wallet_token_balance(
            wallet_address=sender_account.address(),
            token_obj=self.coin_option
        )
        wallet_token_balance_decimals = self.get_amount_decimals(amount=wallet_token_balance,
                                                                 token_obj=self.coin_option)

        if self.config.send_all_balance is True:
            amount_out = wallet_token_balance

        elif wallet_token_balance_decimals < self.config.max_amount_out:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=wallet_token_balance_decimals,
                decimals=self.get_token_decimals(token_obj=self.coin_option)
            )

        else:
            amount_out = self.get_random_amount_out(
                min_amount=self.config.min_amount_out,
                max_amount=self.config.max_amount_out,
                decimals=self.get_token_decimals(token_obj=self.coin_option)
            )

        self.amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                            token_obj=self.coin_option)
        wallet_valid_for_swap = self.check_account_balance_before_transaction(amount_out=amount_out,
                                                                              wallet_address=sender_account.address(),
                                                                              token_obj=self.coin_option)
        if wallet_valid_for_swap is False:
            return None

        transaction_args = [
            TransactionArgument(int(amount_out), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.lend_address}",
            "mint_entry",
            [TypeTag(StructTag.from_str(self.coin_option.contract))],
            transaction_args
        )

        return payload

    def send_mint_transaction(self, private_key: str) -> bool:
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_mint_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        txn_info_message = f"Mint/Lend (Abel finance) {self.amount_out_decimals} {self.coin_option.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        txn_status, txn_status_message = txn_status

        return txn_status
