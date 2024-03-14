import random
import time
from typing import TYPE_CHECKING, Union, Any, Callable

from aptos_sdk.account import Account
from aptos_sdk.account import AccountAddress
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from aptos_sdk.transactions import RawTransaction
from aptos_sdk.transactions import TransactionPayload
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.async_client import ClientConfig
from aptos_sdk.client import ApiError
from loguru import logger

from contracts.base import TokenBase
from aptos_rest_client import CustomRestClient
from src.gecko_pricer import GeckoPricer
from src.storage import Storage
from contracts.tokens.main import Tokens
from src import enums
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.action_models import TransactionSimulationResult
from src.schemas.action_models import TransactionReceipt
from src.schemas.action_models import TransactionPayloadData
from src.execution_storage import ExecutionStorage


if TYPE_CHECKING:
    from src.schemas.tasks.base.swap import SwapTaskBase
    from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
    from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
    from src.schemas.tasks.base.base import TaskBase
    from src.schemas.wallet_data import WalletData


class ModuleBase:
    def __init__(
            self,
            base_url: str,
            task: 'TaskBase',
            account: Account,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):

        self.base_url = base_url
        self.task = task
        self.account = account
        self.client = CustomRestClient(base_url=base_url, proxies=proxies)
        self.gecko_pricer = GeckoPricer(client=self.client)
        self.storage = Storage()
        self.tokens = Tokens()
        self.proxies = proxies
        self.is_task_virtual = getattr(task, 'is_virtual', False)

        self.task = task
        self.wallet_data = wallet_data

        self.execution_storage = ExecutionStorage()

        self.module_execution_result = ModuleExecutionResult()

    def get_random_amount_out_of_token(
            self,
            min_amount,
            max_amount,
            decimals: int
    ) -> int:
        """
        Get random_task amount out of token with decimals
        :param min_amount:
        :param max_amount:
        :param decimals:
        :return:
        """
        random_amount = random.uniform(min_amount, max_amount)
        return int(random_amount * 10 ** decimals)

    def get_address_from_hex(self, hex_address: str):
        """
        Gets address from hex
        :param hex_address:
        :return:
        """
        if hex_address.startswith("0x"):
            hex_address = hex_address[2:]
        return AccountAddress.from_hex(hex_address)

    def get_account(self, private_key: str) -> Account:
        """
        Gets account from private key
        :param private_key:
        :return:
        """
        return Account.load_key(private_key)

    def get_wallet_pub_key(self, private_key: str) -> str:
        """
        Gets wallet public key from private key
        :param private_key:
        :return:
        """
        account = Account.load_key(private_key)
        return account.auth_key()

    def get_wallet_aptos_balance(self, wallet_address: AccountAddress) -> int:
        """
        Gets wallet aptos balance
        :param wallet_address:
        :return:
        """
        try:
            resource = self.client.account_resource(
                wallet_address,
                "0x1::coin::CoinStore<0x1::aptos_coin::AptosCoin>"
            )
            return resource["data"]["coin"]["value"]

        except Exception as ex:
            return 0

    def get_wallet_token_balance(
            self,
            wallet_address: AccountAddress,
            token_address: str,
    ) -> int:
        """
        Gets wallet token balance
        :param wallet_address:
        :param token_address:
        :return:
        """
        try:
            balance = self.client.account_resource(
                wallet_address,
                f"0x1::coin::CoinStore<{token_address}>",
            )
            return int(balance["data"]["coin"]["value"])

        except Exception as ex:
            return 0

    def get_token_info(self, token_obj: TokenBase) -> Union[dict, None]:
        """
        Gets token info
        :param token_obj:
        :return:
        """
        if token_obj.symbol == "aptos":
            return None

        coin_address = self.get_address_from_hex(token_obj.address)
        try:
            token_info = self.client.account_resource(
                coin_address,
                f"0x1::coin::CoinInfo<{token_obj.contract_address}>",
            )
            return token_info["data"]

        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None

    def get_token_decimals(self, token_obj: TokenBase) -> Union[int, None]:
        """
        Gets token decimals
        :param token_obj:
        :return:
        """
        if token_obj.symbol == "aptos":
            return 8

        token_info = self.get_token_info(token_obj=token_obj)
        if not token_info:
            return None

        return token_info["decimals"]

    def make_view_call(
            self,
            function: str,
            type_arguments: list,
            arguments: list
    ) -> Union[Any, None]:
        try:
            payload = {
                "function": function,
                "type_arguments": type_arguments,
                "arguments": arguments,
            }
            response = self.client.client.post(url=f"{self.base_url}/view", json=payload)
            if response.status_code != 200:
                return None

            return response.json()

        except Exception as e:
            logger.debug(f"Error making view call: {e}")
            return None

    def is_token_registered_for_address(
            self,
            wallet_address: AccountAddress,
            token_contract: str
    ):
        """
        Checks if token is registered for address
        :param wallet_address:
        :param token_contract:
        :return:
        """
        try:
            is_registered = self.client.account_resource(
                wallet_address,
                f'0x1::coin::CoinStore<{token_contract}>'
            )
            return True

        except Exception as ex:
            return False

    def register_coin_for_wallet(
            self,
            sender_account: Account,
            token_obj: TokenBase,
    ) -> ModuleExecutionResult:
        """
        Sends coin register transaction
        :param sender_account:
        :param token_obj:
        :return:
        """
        payload = EntryFunction.natural(
            f"0x1::managed_coin",
            "register",
            [TypeTag(StructTag.from_str(token_obj.contract_address))],
            []
        )
        txn_info_message = f"Coin register {token_obj.symbol.upper()} for wallet"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=sender_account,
            txn_payload=payload,
            txn_info_message=txn_info_message
        )

        return txn_status

    def estimate_transaction(
            self,
            raw_transaction: RawTransaction,
            sender_account: Account
    ) -> TransactionSimulationResult:
        """
        Estimates transaction gas usage
        :param raw_transaction:
        :param sender_account:
        :return:
        """
        txn_data = self.client.simulate_transaction(
            transaction=raw_transaction,
            sender=sender_account
        )
        vm_status = txn_data[0]["vm_status"]

        if txn_data[0]["success"] is True:
            result = TransactionSimulationResult(
                result=enums.TransactionStatus.SUCCESS,
                vm_status=vm_status,
                gas_used=int(txn_data[0]["gas_used"])
            )
        else:
            result = TransactionSimulationResult(
                result=enums.TransactionStatus.FAILED,
                vm_status=vm_status,
                gas_used=0
            )

        return result

    def txn_pending_status(self, txn_hash: str) -> bool:
        """
        Checks if transaction is pending
        :param txn_hash:
        :return:
        """
        response = self.client.client.get(f"{self.base_url}/transactions/by_hash/{txn_hash}")

        if response.status_code == 404:
            return True

        elif response.status_code >= 400:
            raise Exception(f"Error getting transaction due RPC error: {response.json()}")

        return response.json()["type"] == "pending_transaction"

    def wait_for_receipt(
            self,
            txn_hash: str,
            timeout: int = 60
    ) -> TransactionReceipt:
        """
        Waits for transaction receipt
        :param txn_hash:
        :param timeout:
        :return:
        """
        start_time = time.time()
        while self.txn_pending_status(txn_hash=txn_hash):
            if time.time() - start_time > timeout:

                return TransactionReceipt(
                    status=enums.TransactionStatus.TIME_OUT,
                    vm_status=None
                )

            time.sleep(1)

        response = self.client.client.get(f"{self.base_url}/transactions/by_hash/{txn_hash}")
        vm_status = response.json().get("vm_status")
        if vm_status is None:
            time.sleep(5)
            response = self.client.client.get(f"{self.base_url}/transactions/by_hash/{txn_hash}")
            vm_status = response.json().get("vm_status")

        if response.json().get("success") is True:
            receipt = TransactionReceipt(
                status=enums.TransactionStatus.SUCCESS,
                vm_status=vm_status
            )
        else:
            receipt = TransactionReceipt(
                status=enums.TransactionStatus.FAILED,
                vm_status=vm_status
            )

        return receipt

    def get_token_reserve(
            self,
            resource_address: AccountAddress,
            payload: str
    ) -> Union[dict, None]:
        """
        Gets token reserve
        :param resource_address:
        :param payload:
        :return:
        """
        try:
            data = self.client.account_resource(
                resource_address,
                payload
            )
            return data

        except Exception as e:
            return None

    def build_raw_transaction(
            self,
            account: Account,
            payload: EntryFunction,
            gas_limit: int,
            gas_price: int
    ) -> RawTransaction:
        """
        Builds raw transaction
        :param account:
        :param payload:
        :param gas_limit:
        :param gas_price:
        :return:
        """
        raw_transaction = RawTransaction(
            sender=account.address(),
            sequence_number=self.client.account_sequence_number(account.address()),
            payload=TransactionPayload(payload),
            max_gas_amount=gas_limit,
            gas_unit_price=gas_price,
            expiration_timestamps_secs=int(time.time()) + 600,
            chain_id=1
        )
        return raw_transaction

    def prebuild_payload_and_estimate_transaction(
            self,
            txn_payload: EntryFunction,
            account: Account,
            gas_limit: int,
            gas_price: int
    ) -> TransactionSimulationResult:
        """
        Prebuilds payload and estimates transaction
        :param txn_payload:
        :param account:
        :param gas_limit:
        :param gas_price:
        :return:
        """
        raw_transaction = self.build_raw_transaction(
            account=account,
            payload=txn_payload,
            gas_limit=gas_limit,
            gas_price=gas_price
        )
        ClientConfig.max_gas_amount = int(gas_limit)

        simulation_result = self.estimate_transaction(
            raw_transaction=raw_transaction,
            sender_account=account
        )

        return simulation_result

    def build_txn_payload_data(self) -> TransactionPayloadData:
        """
        ABC method for building transaction payload data. Must be implemented in child classes.
        :return:
        """
        raise NotImplementedError

    def build_reverse_txn_payload_data(self) -> TransactionPayloadData:
        """
        ABC method for building reverse transaction payload data. Must be implemented in child classes.
        :return:
        """
        raise NotImplementedError

    def send_txn(self) -> ModuleExecutionResult:
        """
        ABC method for sending a transaction. Must be implemented in child classes.
        :return:
        """
        raise NotImplementedError

    def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Tries to send a transaction.
        :param retries:
        :return:
        """
        result: ModuleExecutionResult = self.module_execution_result

        if not isinstance(retries, int):
            logger.error(f"Retries must be an integer, got {retries}, setting to 1")
            retries = 1

        for i in range(retries):
            logger.info(f"Attempt {i + 1}/{retries}")

            result = self.send_txn()

            if self.task.test_mode is True:
                return result

            if result.execution_status == enums.ModuleExecutionStatus.RETRY:
                continue

            if (result.execution_status == enums.ModuleExecutionStatus.SUCCESS or
                    result.execution_status == enums.ModuleExecutionStatus.SENT):
                return result

            time.sleep(1)
        else:
            logger.error(f"Failed to send txn after {retries} attempts")
            return result

    def submit_bcs_transaction(self, signed_transaction):
        try:
            tx_hash = self.client.submit_bcs_transaction(signed_transaction)
            return tx_hash
        except ApiError as e:
            logger.error(f"ApiError: {e}")
            return None

    def simulate_and_send_transfer_type_transaction(
            self,
            account: Account,
            txn_payload: EntryFunction,
            txn_info_message: str
    ) -> ModuleExecutionResult:
        """
        Simulates and sends transfer type transaction
        :param account:
        :param txn_payload:
        :param txn_info_message:
        :return:
        """
        if txn_info_message:
            logger.warning(f"Action: {txn_info_message}")

        simulation_status = self.prebuild_payload_and_estimate_transaction(
            account=account,
            txn_payload=txn_payload,
            gas_limit=int(self.task.gas_limit),
            gas_price=int(self.task.gas_price)
        )

        if simulation_status.result == enums.TransactionStatus.FAILED:
            err_msg = f"Transaction simulation failed. Status: {simulation_status.vm_status}"
            logger.error(err_msg)
            return self.module_execution_result

        logger.success(f"Transaction simulation success. Gas used: {simulation_status.gas_used}")

        if self.task.forced_gas_limit is True:
            gas_limit = int(self.task.gas_limit)
        else:
            if int(simulation_status.gas_used) <= 200:
                gas_limit = int(int(simulation_status.gas_used) * 2)
            else:
                gas_limit = int(int(simulation_status.gas_used) * 1.15)

        self.client.client_config.max_gas_amount = gas_limit

        if self.task.test_mode is True:
            logger.info(f"Test mode enabled. Skipping transaction")
            return self.module_execution_result

        signed_transaction = self.client.create_bcs_signed_transaction(
            sender=account,
            payload=TransactionPayload(txn_payload)
        )
        tx_hash = self.submit_bcs_transaction(signed_transaction=signed_transaction)
        if tx_hash is None:
            err_msg = f"Transaction submission failed"
            logger.error(err_msg)
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.FAILED.value
            return self.module_execution_result

        if self.task.wait_for_receipt is True:
            logger.info(
                f"Txn sent. Waiting for receipt (Timeout in {self.task.txn_wait_timeout_sec}s)."
                f" Txn Hash: {tx_hash}"
            )
            txn_receipt = self.wait_for_receipt(
                txn_hash=tx_hash,
                timeout=self.task.txn_wait_timeout_sec
            )

            if txn_receipt.status == enums.TransactionStatus.SUCCESS:
                msg = f"Transaction success, vm status: {txn_receipt.vm_status}. Txn Hash: {tx_hash}"
                logger.success(msg)
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.SUCCESS.value
                self.module_execution_result.execution_info = msg
                self.module_execution_result.hash = tx_hash
                return self.module_execution_result

            elif txn_receipt.status == enums.TransactionStatus.FAILED:
                msg = f"Transaction failed, vm status: {txn_receipt.vm_status}. Txn Hash: {tx_hash}"
                logger.error(msg)
                logger.error(msg)
                self.module_execution_result.hash = tx_hash

            elif txn_receipt.status == enums.TransactionStatus.TIME_OUT:
                msg = f"Transaction timeout, vm status: {txn_receipt.vm_status}. Txn Hash: {tx_hash}"
                logger.error(msg)
                self.module_execution_result.hash = tx_hash

        else:
            msg = f"Transaction sent. Txn Hash: {tx_hash}"
            logger.success(msg)
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.SENT.value
            self.module_execution_result.execution_info = msg
            self.module_execution_result.hash = tx_hash

        return self.module_execution_result


class SingleCoinModuleBase(ModuleBase):
    def __init__(
            self,
            account: Account,
            base_url: str,
            task,
            wallet_data: 'WalletData',
            proxies: dict = None,
    ):
        super().__init__(
            base_url=base_url,
            task=task,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )
        random_coin_y = getattr(self.task, "random_coin_y", None)
        if not random_coin_y == enums.MiscTypes.RANDOM:
            coin_x_symbol = getattr(self.task, "coin_x")
            self.coin_x = self.tokens.get_by_name(coin_x_symbol)
            self.token_x_decimals = self.get_token_decimals(token_obj=self.coin_x)

            if not self.is_task_virtual:

                self.initial_balance_x_wei = self.get_wallet_token_balance(
                    wallet_address=self.account.address(),
                    token_address=self.coin_x.contract_address
                )

    async def set_fetched_data_to_exec_storage(self):
        """
        Sets fetched data to execution storage
        :return:
        """
        self.execution_storage.set_pre_execution_data(
            wallet_id=self.wallet_data.wallet_id,
            task_id=self.task.task_id,
            data={
                'initial_balance_x_wei': self.initial_balance_x_wei,
            },
        )

    def check_local_tokens_data(self) -> bool:
        """
        Checks if token decimals are fetched.
        :return:
        """

        if self.token_x_decimals is None:
            logger.error(f"Token decimals not fetched")
            return False

    def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase,
    ) -> Union[int, None]:
        """
        Calculates amount out of token with decimals
        :param coin_x:
        :return:
        """
        initial_balance_x_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals

        if self.initial_balance_x_wei == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance = 0")
            return None

        use_all_balance = getattr(self.task, "use_all_balance", None)
        send_percent_balance = getattr(self.task, "send_percent_balance", None)
        min_amount_out = getattr(self.task, "min_amount_out", None)
        max_amount_out = getattr(self.task, "max_amount_out", None)

        if use_all_balance:
            amount_out_wei = self.initial_balance_x_wei

        elif send_percent_balance:
            percent = random.randint(
                int(min_amount_out), int(max_amount_out)
            ) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

        elif initial_balance_x_decimals < min_amount_out:
            err_msg = (
                f"Wallet {coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {initial_balance_x_decimals}, min amount out: {min_amount_out}"
            )
            logger.error(err_msg)
            return None

        elif initial_balance_x_decimals < max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=initial_balance_x_decimals,
                decimals=self.token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=max_amount_out,
                decimals=self.token_x_decimals
            )

        return amount_out_wei


class MultiCoinModuleBase(ModuleBase):
    def __init__(
            self,
            account: Account,
            base_url: str,
            task,
            wallet_data: 'WalletData',
            proxies: dict = None,
    ):
        super().__init__(
            base_url=base_url,
            task=task,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )
        super().__init__(
            base_url=base_url,
            task=task,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

        random_coin_y = getattr(task, "random_coin_y", None)
        if not random_coin_y == enums.MiscTypes.RANDOM:

            coin_x_symbol = getattr(self.task, "coin_x")
            coin_y_symbol = getattr(self.task, "coin_y")

            self.coin_x = self.tokens.get_by_name(coin_x_symbol)
            self.token_x_decimals = self.get_token_decimals(token_obj=self.coin_x)

            self.coin_y = self.tokens.get_by_name(coin_y_symbol)
            self.token_y_decimals = self.get_token_decimals(token_obj=self.coin_y)

            if not self.is_task_virtual:

                # COIN X
                self.initial_balance_x_wei = self.get_wallet_token_balance(
                    wallet_address=self.account.address(),
                    token_address=self.coin_x.contract_address
                )

                # COIN Y
                self.initial_balance_y_wei = self.get_wallet_token_balance(
                    wallet_address=self.account.address(),
                    token_address=self.coin_y.contract_address
                )

    def set_fetched_data_to_exec_storage(self):
        """
        Sets fetched data to execution storage
        :return:
        """
        if not self.task.is_virtual:

            self.execution_storage.set_pre_execution_data(
                wallet_id=self.wallet_data.wallet_id,
                task_id=self.task.task_id,
                data={
                    'initial_balance_x_wei': self.initial_balance_x_wei,
                    'initial_balance_y_wei': self.initial_balance_y_wei
                },
            )

    def check_local_tokens_data(self) -> bool:
        """
        Checks if token decimals are fetched.
        :return:
        """
        if self.token_x_decimals is None or self.token_y_decimals is None:
            logger.error(f"Token decimals not fetched")
            return False

    def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase,
    ) -> Union[int, None]:
        """
        Calculates amount out of token with decimals
        :param coin_x:
        :return:
        """
        initial_balance_x_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals

        if self.initial_balance_x_wei == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance = 0")
            return None

        use_all_balance = getattr(self.task, "use_all_balance", None)
        send_percent_balance = getattr(self.task, "send_percent_balance", None)
        min_amount_out = getattr(self.task, "min_amount_out", None)
        max_amount_out = getattr(self.task, "max_amount_out", None)

        if use_all_balance:
            amount_out_wei = self.initial_balance_x_wei

        elif send_percent_balance:
            percent = random.randint(
                int(min_amount_out), int(max_amount_out)
            ) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

        elif initial_balance_x_decimals < min_amount_out:
            err_msg = (
                f"Wallet {coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {initial_balance_x_decimals}, min amount out: {min_amount_out}"
            )
            logger.error(err_msg)
            return None

        elif initial_balance_x_decimals < max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=initial_balance_x_decimals,
                decimals=self.token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=min_amount_out,
                max_amount=max_amount_out,
                decimals=self.token_x_decimals
            )

        return amount_out_wei


class SwapModuleBase(MultiCoinModuleBase):
    task: 'SwapTaskBase'

    def __init__(
            self,
            account: Account,
            base_url: str,
            task: 'SwapTaskBase',
            wallet_data: 'WalletData',
            proxies: dict = None,
    ):
        super().__init__(
            base_url=base_url,
            task=task,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

        if self.task.is_virtual:

            # COIN X
            self.coin_x = self.tokens.get_by_name(self.task.coin_y)
            self.initial_balance_x_wei = self.execution_storage.get_by_wallet_id_and_task_id(
                wallet_id=self.wallet_data.wallet_id,
                task_id=self.task.task_id
            ).get('initial_balance_y_wei')
            self.token_x_decimals = self.get_token_decimals(token_obj=self.coin_x)

            # COIN Y
            self.coin_y = self.tokens.get_by_name(self.task.coin_x)
            self.initial_balance_y_wei = self.execution_storage.get_by_wallet_id_and_task_id(
                wallet_id=self.wallet_data.wallet_id,
                task_id=self.task.task_id
            ).get('initial_balance_x_wei')
            self.token_y_decimals = self.get_token_decimals(token_obj=self.coin_y)

            self.build_transaction_payload: Callable = self.build_reverse_txn_payload_data

    def send_txn(self) -> ModuleExecutionResult:
        """
        Sends transaction
        :return:
        """

        self.set_fetched_data_to_exec_storage()

        if self.check_local_tokens_data() is False:
            logger.error(f"Failed to fetch local tokens data in swap module")
            return self.module_execution_result

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            logger.error(f"Failed to build transaction payload data")
            return self.module_execution_result

        out_decimals = txn_payload_data.amount_x_decimals
        in_decimals = txn_payload_data.amount_y_decimals

        coin_x_symbol = self.coin_x.symbol.upper()
        coin_y_symbol = self.coin_y.symbol.upper()

        module_name = self.task.module_name.title()
        txn_info_message = f"Swap ({module_name}) | " \
                           f"{out_decimals} ({coin_x_symbol}) -> " \
                           f"{in_decimals} ({coin_y_symbol}). " \
                           f"Slippage: {self.task.slippage}%."

        logger.warning(txn_info_message)

        if self.task.compare_with_cg_price:
            coin_x_cg_id = self.tokens.get_cg_id_by_name(coin_x_symbol)
            coin_y_cg_id = self.tokens.get_cg_id_by_name(coin_y_symbol)

            max_price_difference_percent: Union[float, int] = self.task.max_price_difference_percent
            swap_price_validation_data = self.gecko_pricer.is_target_price_valid(
                x_token_id=coin_x_cg_id,
                y_token_id=coin_y_cg_id,
                x_amount=out_decimals,
                y_amount=in_decimals,
                max_price_difference_percent=max_price_difference_percent
            )
            is_price_valid, price_data = swap_price_validation_data
            if not is_price_valid:
                logger.error(
                    f"Swap rate is not valid ({module_name}). "
                    f"Gecko rate: {price_data['gecko_price']}, "
                    f"Swap rate: {price_data['target_price']}"
                )

                return self.module_execution_result

            logger.info(
                f"Swap rate is valid ({module_name}). "
                f"Gecko rate: {price_data['gecko_price']}, "
                f"Swap rate: {price_data['target_price']}."
            )

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=""
        )

        return txn_status


class LiquidityModuleBase(MultiCoinModuleBase):
    task: Union['AddLiquidityTaskBase', 'RemoveLiquidityTaskBase']

    def __init__(
            self,
            account: Account,
            base_url: str,
            task: Union['AddLiquidityTaskBase', 'RemoveLiquidityTaskBase'],
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            base_url=base_url,
            task=task,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

    def send_txn(self) -> ModuleExecutionResult:
        """
          Sends transaction
        :return:
        """

        self.set_fetched_data_to_exec_storage()

        if self.check_local_tokens_data() is False:
            logger.error(f"Failed to fetch local tokens data in swap module")
            return self.module_execution_result

        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            logger.error(f"Failed to build transaction payload data")
            return self.module_execution_result

        module_name = self.task.module_name.title()
        module_type = ("Add liquidity" if self.task.module_type == enums.ModuleType.LIQUIDITY_ADD
                       else "Remove liquidity")

        txn_info_message = f"{module_type} ({module_name}) | " \
                           f"{txn_payload_data.amount_x_decimals} ({self.coin_x.symbol.upper()}) + " \
                           f"{txn_payload_data.amount_y_decimals} ({self.coin_y.symbol.upper()}). " \
                           f"Slippage: {self.task.slippage}%."

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )

        return txn_status
