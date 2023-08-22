from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)

from aptos_sdk.account import (Account,
                               AccountAddress)


from loguru import logger

from modules.base import AptosBase
from contracts.tokens import Tokens


from src.schemas.delegation import DelegateConfigSchema


class Delegate(AptosBase):
    DELEGATION_POOL_ADDRESS = "0x1::delegation_pool"
    MIN_DELEGATION_AMOUNT_DECIMALS = 11

    def __init__(self, config, base_url: str, proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.tokens = Tokens()
        self.config: DelegateConfigSchema = config

        self.src_coin = self.tokens.get_by_name("Aptos")

        self.amount_out_decimals = None

    def build_delegation_transaction_payload(self, sender_account: Account):
        wallet_token_balance = self.get_wallet_token_balance(wallet_address=sender_account.address(),
                                                             token_obj=self.src_coin)
        src_coin_decimals = self.get_token_decimals(self.src_coin)
        wallet_token_balance_decimals = wallet_token_balance / 10 ** src_coin_decimals

        if wallet_token_balance is None:
            logger.error("Error getting wallet token balance")
            return None

        if wallet_token_balance == 0:
            logger.error(f"Wallet token balance is 0: "
                         f"{wallet_token_balance_decimals} {self.src_coin.symbol.upper}")
            return None

        min_delegation_amount = self.MIN_DELEGATION_AMOUNT_DECIMALS * 10 ** src_coin_decimals

        if wallet_token_balance < min_delegation_amount:
            logger.error(f"Wallet token balance is less than min delegation amount (11): "
                         f"{wallet_token_balance_decimals} {self.src_coin.symbol.upper()}")
            return None

        amount_out = self.get_random_amount_out(min_amount=self.config.min_amount_out,
                                                max_amount=self.config.max_amount_out,
                                                decimals=src_coin_decimals)
        self.amount_out_decimals = amount_out / 10 ** src_coin_decimals

        if amount_out is None:
            logger.error("Error getting random amount out")
            return None

        if amount_out > wallet_token_balance:
            logger.error(f"Amount out is greater than wallet token balance: "
                         f"{self.amount_out_decimals} > {wallet_token_balance_decimals}")
            return None
        validator_address = AccountAddress.from_hex(self.config.validator_addr)

        transaction_args = [
            TransactionArgument(validator_address, Serializer.struct),
            TransactionArgument(int(amount_out), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.DELEGATION_POOL_ADDRESS}",
            "add_stake",
            [],
            transaction_args
        )

        return payload

    def send_delegation_transaction(self, private_key: str) -> bool:
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_delegation_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        txn_info_message = (
            f"Delegation (Add stake) - "
            f"{round(self.amount_out_decimals, 4)} ({self.src_coin.symbol.upper()}),"
            f" validator address: {self.config.validator_addr}."
        )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        txn_status, txn_status_message = txn_status

        return txn_status

