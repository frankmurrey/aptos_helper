import time

from modules.base import AptosBase

from contracts.tokens import (Tokens,
                              Token)

from aptos_sdk.transactions import (EntryFunction,
                                    TransactionPayload)
from aptos_sdk.type_tag import TypeTag, StructTag
from aptos_sdk.account import Account

from aptos_rest_client.client import ClientConfig

from src.schemas.aptos_bridge import ClaimConfigSchema

from loguru import logger


class BridgedTokenClaimer(AptosBase):
    def __init__(self,
                 base_url: str,
                 config: ClaimConfigSchema,
                 proxies: dict = None):
        super().__init__(base_url=base_url, proxies=proxies)
        self.config = config
        self.base_url = base_url
        self.available_tokens = Tokens().get_aptos_bridge_available_coins()

    def get_unclaimed_amount_of_token_for_address(self,
                                                  address: str,
                                                  token_handle: str) -> int:
        url = f"{self.base_url}/tables/{token_handle}/item"
        payload = {
            "key_type": "address",
            "value_type": "u64",
            "key": address
        }
        response = self.client.post(url, json=payload)
        if response.status_code == 200:
            unclaimed_amount = response.json()
        else:
            unclaimed_amount = 0
        return unclaimed_amount

    def get_all_unclaimed_tokens_for_address(self, address: str) -> list:
        unclaimed_token_objects = []

        for token in self.available_tokens:
            unclaimed_amount = self.get_unclaimed_amount_of_token_for_address(
                address=address,
                token_handle=token.aptos_bridge_handle
            )
            if unclaimed_amount != 0:
                unclaimed_token_objects.append(token)

        return unclaimed_token_objects

    def build_claim_txn_payload(self, token_contract: Token):
        payload = EntryFunction.natural(
            f"0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::coin_bridge",
            "claim_coin",
            [TypeTag(StructTag.from_str(token_contract.contract))],
            []
        )

        return payload

    def claim(self,
              sender_account: Account,
              token_contract: Token):
        txn_payload = self.build_claim_txn_payload(token_contract=token_contract)
        if not txn_payload:
            return False

        raw_transaction = self.build_raw_transaction(
            sender_account=sender_account,
            payload=txn_payload,
            gas_limit=int(self.config.gas_limit),
            gas_price=int(self.config.gas_price)
        )
        ClientConfig.max_gas_amount = int(int(self.config.gas_limit) * 1.2)

        simulate_txn = self.estimate_transaction(raw_transaction=raw_transaction,
                                                 sender_account=sender_account)

        if simulate_txn is not True:
            if simulate_txn is False:
                logger.error(f"Can't simulate transaction: claim {token_contract.name}")
                return False
            else:
                logger.error(f"Transaction simulation failed. Status: {simulate_txn}")
                return False
        else:
            logger.success(f"Transaction simulation success: claim {token_contract.name}")

        if self.config.test_mode is True:
            return False

        signed_transaction = self.create_bcs_signed_transaction(sender=sender_account,
                                                                payload=TransactionPayload(txn_payload))
        tx_hash = self.submit_bcs_transaction(signed_transaction)

        if self.config.wait_for_receipt is True:
            logger.debug(f"Txn sent. Waiting for receipt (Timeout in {self.config.txn_wait_timeout_sec}s)."
                         f" Txn Hash: {tx_hash}")
            txn_receipt = self.wait_for_receipt(txn_hash=tx_hash,
                                                timeout=self.config.txn_wait_timeout_sec)

            if txn_receipt is True:
                logger.success(f"Transaction success: claim {token_contract.name}"
                               f" Txn Hash: {tx_hash}")
                return True
            elif txn_receipt is False:
                logger.error(f"Transaction failed. Txn Hash: {tx_hash}")
                return False
            elif txn_receipt is None:
                logger.error(f"Time out {self.config.txn_wait_timeout_sec},"
                             f" txn not included in blockchain. Txn Hash: {tx_hash}")
                return False
        else:
            logger.success(f"Transaction sent. Txn Hash: {tx_hash}")
            return True

    def claim_batch(self, private_key: str):
        sender_account = self.get_account(private_key=private_key)
        tokens_to_claim = self.get_all_unclaimed_tokens_for_address(address=str(sender_account.address()))
        if not tokens_to_claim:
            logger.warning("Nothing to claim")
            return False

        last_status = False
        for token in tokens_to_claim:
            last_status = self.claim(sender_account=sender_account,
                                     token_contract=token)
            time.sleep(2)

        return last_status

