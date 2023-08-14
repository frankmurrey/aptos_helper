import random
import time
from datetime import datetime

from contracts.base import Token

from src.schemas.wallet_log import WalletActionSchema
from src.action_logger import (ActionLogger,
                               log_all_actions_to_xlsx)

from aptos_rest_client import CustomRestClient
from aptos_rest_client.client import (ResourceNotFound,
                                      ClientConfig)

from aptos_sdk.account import (Account,
                               AccountAddress)
from aptos_sdk.type_tag import (TypeTag,
                                StructTag)
from aptos_sdk.transactions import (RawTransaction,
                                    TransactionPayload,
                                    EntryFunction)

from loguru import logger


class AptosBase(CustomRestClient):
    def __init__(self, base_url: str, proxies: dict = None):
        self.proxies = proxies
        super().__init__(base_url=base_url, proxies=proxies)

    def get_random_amount_out(self,
                              min_amount,
                              max_amount,
                              decimals: int) -> int:
        random_amount = random.uniform(min_amount, max_amount)
        return int(random_amount * 10 ** decimals)

    def check_account_balance_before_transaction(self,
                                                 amount_out: int,
                                                 wallet_address: AccountAddress,
                                                 token_obj: Token,
                                                 ) -> bool:
        try:
            wallet_aptos_balance = self.get_wallet_aptos_balance(wallet_address=wallet_address)
            wallet_token_balance = self.get_wallet_token_balance(wallet_address=wallet_address,
                                                                 token_obj=token_obj)

            if wallet_aptos_balance is None or wallet_token_balance is None:
                return False

            if wallet_aptos_balance == 0:
                logger.error("Wallet aptos balance is 0")
                return False

            if wallet_token_balance == 0:
                logger.error("Wallet token balance is 0")
                return False

            if wallet_token_balance < amount_out:
                wallet_token_balance_decimals = self.get_amount_decimals(amount=wallet_token_balance,
                                                                         token_obj=token_obj)
                amount_out_decimals = self.get_amount_decimals(amount=amount_out,
                                                               token_obj=token_obj)
                logger.error(f"Wallet {token_obj.name.title()} balance is less than amount out."
                             f" Balance: {wallet_token_balance_decimals}, amount out: {amount_out_decimals}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking wallet balance: {e}")
            return False

    def get_amount_decimals(self,
                            amount: int,
                            token_obj: Token) -> float:
        return round(amount * 10 ** -(self.get_token_decimals(token_obj=token_obj)), 4)

    def get_address_from_hex(self,
                             hex_address: str):

        if hex_address.startswith("0x"):
            hex_address = hex_address[2:]
        return AccountAddress(bytes.fromhex(hex_address))

    def get_account(self, private_key: str) -> Account:
        return Account.load_key(private_key)

    def get_wallet_address(self,
                           private_key: str):

        account = Account.load_key(private_key)
        return account.address()

    def get_wallet_pub_key(self,
                           private_key: str):

        account = Account.load_key(private_key)
        return account.auth_key()

    def get_wallet_aptos_balance(self, wallet_address: AccountAddress):
        try:
            resource = self.account_resource(
                wallet_address,
                "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>"
            )
            return resource["data"]["coin"]["value"]
        except ResourceNotFound:
            return 0

    def get_wallet_token_balance(self,
                                 wallet_address: AccountAddress,
                                 token_obj: Token = None,
                                 token_contract=None):
        if not token_obj and not token_contract:
            logger.error("Please provide token_obj or token_contract")
            return None

        if token_obj:
            token_contract = token_obj.contract
        else:
            token_contract = token_contract

        try:
            balance = self.account_resource(
                wallet_address,
                f"0x1::coin::CoinStore<{token_contract}>",
            )
            return int(balance["data"]["coin"]["value"])
        except ResourceNotFound:
            return 0

    def get_token_info(self,
                       token_obj: Token):
        if token_obj.symbol == "aptos":
            return None

        coin_address = self.get_address_from_hex(token_obj.address)

        try:
            token_info = self.account_resource(
                coin_address,
                f"0x1::coin::CoinInfo<{token_obj.contract}>",
            )
            return token_info["data"]
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None

    def get_token_decimals(self,
                           token_obj: Token):

        if token_obj.symbol == "aptos":
            return 8
        token_info = self.get_token_info(token_obj=token_obj)
        if not token_info:
            return None

        return token_info["decimals"]

    def is_token_registered_for_address(self,
                                        wallet_address: AccountAddress,
                                        token_contract):
        try:
            is_registered = self.account_resource(
                wallet_address,
                f'0x1::coin::CoinStore<{token_contract}>'
            )

            return True
        except ResourceNotFound:
            return False

    def register_coin_for_wallet(self,
                                 sender_account: Account,
                                 token_obj,
                                 config):
        payload = EntryFunction.natural(
            f"0x1::managed_coin",
            "register",
            [TypeTag(StructTag.from_str(token_obj.contract))],
            []
        )
        txn_info_message = f"Coin register {token_obj.symbol.upper()} for wallet"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            config=config,
            sender_account=sender_account,
            txn_payload=payload,
            txn_info_message=txn_info_message
        )

        return txn_status

    def estimate_transaction(self,
                             raw_transaction: RawTransaction,
                             sender_account: Account):
        txn_data = self.simulate_transaction(transaction=raw_transaction,
                                             sender=sender_account)
        vm_status = txn_data[0]["vm_status"]

        if txn_data[0]["success"] is True:
            return True, txn_data[0]["gas_used"]
        else:
            return False, vm_status

    def txn_pending_status(self,
                           txn_hash: str):
        response = self.client.get(f"{self.base_url}/transactions/by_hash/{txn_hash}")
        if response.status_code == 404:
            return True
        if response.status_code >= 400:
            raise Exception(f"Error getting transaction due RPC error: {response.json()}")
        return response.json()["type"] == "pending_transaction"

    def wait_for_receipt(self,
                         txn_hash: str,
                         timeout: int = 60):
        start_time = time.time()
        while self.txn_pending_status(txn_hash=txn_hash):
            if time.time() - start_time > timeout:
                logger.error(f"Timeout waiting for transaction receipt: {txn_hash}")
                return None

            time.sleep(1)

        response = self.client.get(f"{self.base_url}/transactions/by_hash/{txn_hash}")
        vm_status = response.json().get("vm_status")
        if response.json().get("success") is True:
            return True, vm_status
        else:
            return False, vm_status

    def build_raw_transaction(self,
                              sender_account: Account,
                              payload: EntryFunction,
                              gas_limit: int,
                              gas_price: int) -> RawTransaction:

        raw_transaction = RawTransaction(
            sender=sender_account.address(),
            sequence_number=self.account_sequence_number(sender_account.address()),
            payload=TransactionPayload(payload),
            max_gas_amount=gas_limit,
            gas_unit_price=gas_price,
            expiration_timestamps_secs=int(time.time()) + 600,
            chain_id=1
        )
        return raw_transaction

    def get_token_reserve(self,
                          resource_address,
                          payload):
        try:
            data = self.account_resource(
                resource_address,
                payload
            )
            return data

        except ResourceNotFound:
            return None

        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def prebuild_payload_and_estimate_transaction(self,
                                                  txn_payload,
                                                  sender_account,
                                                  gas_limit,
                                                  gas_price):
        raw_transaction = self.build_raw_transaction(sender_account=sender_account,
                                                     payload=txn_payload,
                                                     gas_limit=gas_limit,
                                                     gas_price=gas_price)
        ClientConfig.max_gas_amount = int(gas_limit)

        simulate_txn: tuple = self.estimate_transaction(raw_transaction=raw_transaction,
                                                        sender_account=sender_account)

        is_simulation_success = simulate_txn[0]
        simulation_status_data = simulate_txn[1]

        if is_simulation_success is not True:
            logger.error(f"Transaction simulation failed. Status: {simulation_status_data}")
            return None
        else:
            logger.success(f"Transaction simulation success, gas used: {simulation_status_data}")
            return simulation_status_data

    def simulate_and_send_transfer_type_transaction(self,
                                                    config,
                                                    sender_account: Account,
                                                    txn_payload: EntryFunction,
                                                    txn_info_message: str
                                                    ):
        current_proxy_body = None
        if self.proxies:
            current_proxy = self.proxies.get('http://')
            current_proxy_body = current_proxy.split("://")[1]

        logger.warning(f"Action: {txn_info_message}")

        wallet_log = WalletActionSchema(
            wallet_address=str(sender_account.address()),
            date_time=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            action_type=txn_info_message,
            proxy=current_proxy_body)

        simulated_raw_transaction_gas_estimate = self.prebuild_payload_and_estimate_transaction(
            sender_account=sender_account,
            txn_payload=txn_payload,
            gas_limit=int(config.gas_limit),
            gas_price=int(config.gas_price)
        )

        if simulated_raw_transaction_gas_estimate is None:
            return False

        if config.force_gas_limit is True:
            gas_limit = int(config.gas_limit)
        else:
            gas_limit = int(int(simulated_raw_transaction_gas_estimate) * 1.1)
        ClientConfig.max_gas_amount = gas_limit

        if config.test_mode is True:
            logger.debug(f"Test mode enabled. Skipping transaction")
            return False

        signed_transaction = self.create_bcs_signed_transaction(sender=sender_account,
                                                                payload=TransactionPayload(txn_payload))
        tx_hash = self.submit_bcs_transaction(signed_transaction)

        if config.wait_for_receipt is True:
            logger.debug(f"Txn sent. Waiting for receipt (Timeout in {config.txn_wait_timeout_sec}s)."
                         f" Txn Hash: {tx_hash}")
            txn_receipt = self.wait_for_receipt(txn_hash=tx_hash,
                                                timeout=config.txn_wait_timeout_sec)
            txn_status = txn_receipt[0]
            vm_status = txn_receipt[1]

            wallet_log.transaction_hash = tx_hash
            wallet_log.is_success = txn_status

            action_logger = ActionLogger(action_data=wallet_log)
            action_logger.log_action()
            log_all_actions_to_xlsx()

            if txn_status is True:
                logger.success(f"Transaction success, vm status: {vm_status}."
                               f" Txn Hash: {tx_hash}")
                return True
            elif txn_status is False:
                logger.error(f"Transaction failed, vm status: {vm_status}. Txn Hash: {tx_hash}")
                return False
        else:
            wallet_log.transaction_hash = tx_hash
            wallet_log.is_success = None

            action_logger = ActionLogger(action_data=wallet_log)
            action_logger.log_action()
            log_all_actions_to_xlsx()

            logger.success(f"Transaction sent:"
                           f" Txn Hash: {tx_hash}")
            return True


