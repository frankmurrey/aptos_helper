from aptos_sdk.transactions import (EntryFunction,
                                    TransactionArgument,
                                    Serializer)

from aptos_sdk.account import (Account,
                               AccountAddress)


from loguru import logger

from modules.base import AptosBase
from contracts.tokens import Tokens


from src.schemas.delegation import UnlockConfigSchema


class Unlock(AptosBase):
    DELEGATION_POOL_ADDRESS = "0x1::delegation_pool"
    MIN_DELEGATION_AMOUNT_DECIMALS = 11

    def __init__(self, config, base_url: str, proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.tokens = Tokens()
        self.config: UnlockConfigSchema = config

        self.src_coin = self.tokens.get_by_name("Aptos")

        self.amount_in_decimals = None

    def get_current_staked_balance(self,
                                   wallet_address: AccountAddress,
                                   validator_address: AccountAddress):
        url = f"{self.base_url}/view"
        payload = {
            "function": "0x1::delegation_pool::get_stake",
            "type_arguments": [],
            "arguments": [str(validator_address),
                          str(wallet_address)],
        }
        response = self.client.post(url=url, json=payload)
        if response.status_code != 200:
            logger.error(f"Error getting current staked balance: {response.text}")
            return None

        response_json = response.json()

        return int(response_json[0])

    def build_unlock_transaction_payload(self, sender_account: Account):
        wallet_address = sender_account.address()
        validator_address = AccountAddress.from_hex(self.config.validator_addr)

        current_staked_balance = self.get_current_staked_balance(wallet_address=wallet_address,
                                                                 validator_address=validator_address)

        if current_staked_balance is None:
            return None

        if current_staked_balance == 0:
            logger.error(f"Current staked balance is 0")
            return None

        amount_in = current_staked_balance
        self.amount_in_decimals = amount_in / 10 ** self.get_token_decimals(self.src_coin)

        transaction_args = [
            TransactionArgument(validator_address, Serializer.struct),
            TransactionArgument(int(amount_in), Serializer.u64),
        ]

        payload = EntryFunction.natural(
            f"{self.DELEGATION_POOL_ADDRESS}",
            "unlock",
            [],
            transaction_args
        )

        return payload

    def send_unlock_transaction(self, private_key: str):
        sender_account = self.get_account(private_key=private_key)
        txn_payload = self.build_unlock_transaction_payload(sender_account=sender_account)

        if txn_payload is None:
            return False

        txn_info_message = (
            f"Unlock (Unstake delegation) - "
            f"{round(self.amount_in_decimals, 4)} ({self.src_coin.symbol.upper()}),"
            f" validator address: {self.config.validator_addr}."
        )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=self.config,
            sender_account=sender_account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        return txn_status


if __name__ == '__main__':
    config = UnlockConfigSchema(
        validator_addr="0x9bfd93ebaa1efd65515642942a607eeca53a0188c04c21ced646d2f0b9f551e8",
        test_mode=False,
        gas_price=100,
        gas_limit=20000,
        wait_for_receipt=True,
        txn_wait_timeout_seconds=60
    )

    unlock = Unlock(config=config,
                    base_url="https://rpc.ankr.com/http/aptos/v1",
                    proxies=None)
    unlock.send_unlock_transaction(
        private_key='0x34ecbdfa94c5507027319cf5cf79ba04fab775b3055bf5d629cd0ff929cc72ca')