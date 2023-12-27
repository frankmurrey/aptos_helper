from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from aptos_sdk.client import ResourceNotFound
from loguru import logger

from modules.base import ModuleBase
from src.schemas.tasks.base.withdraw import WithdrawTaskBase
from src import enums
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.wallet_data import WalletData


class AbleFinanceRedeem(ModuleBase):
    store_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin::ACoinStore"
    lend_address: str = "0xc0188ad3f42e66b5bd3596e642b8f72749b67d84e6349ce325b27117a9406bdf::acoin_lend"

    def __init__(
            self,
            account: Account,
            task: WithdrawTaskBase,
            base_url: str,
            wallet_data: WalletData,
            proxies: dict = None
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )
        self.coin_x = self.tokens.get_by_name(task.coin_x)

        self.account = account
        self.task = task

    def get_max_redeem_amount(
            self,
            coin_contract: str,
            account_address: AccountAddress
    ):
        try:
            resource_type = f"{self.store_address}<{coin_contract}>"

            data = self.client.account_resource(
                account_address,
                resource_type
            )

            return data.get('data').get('coin').get('value')

        except Exception as ex:
            logger.error(f"LP not found on wallet balance")
            return None

    def build_transaction_payload(self):
        max_redeem_amount = self.get_max_redeem_amount(
            coin_contract=self.coin_x.contract_address,
            account_address=self.account.address()
        )
        if max_redeem_amount is None:
            logger.error("LP not found on wallet balance")
            return None

        max_redeem_amount = int(max_redeem_amount)
        if max_redeem_amount == 0:
            logger.error("Nothing to redeem (claim)")
            return None

        transaction_args = [
            TransactionArgument(int(max_redeem_amount), Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.lend_address}",
            "redeem_entry",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address))
            ],
            transaction_args
        )

        return payload

    def send_txn(self) -> ModuleExecutionResult:
        txn_payload = self.build_transaction_payload()
        if txn_payload is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"Redeem (Abel finance) - coin: {self.coin_x.symbol.upper()}"

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload,
            txn_info_message=txn_info_message
        )

        return txn_status
