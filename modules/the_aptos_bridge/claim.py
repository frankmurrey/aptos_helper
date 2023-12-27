from typing import TYPE_CHECKING

from aptos_sdk.transactions import EntryFunction
from aptos_sdk.type_tag import TypeTag, StructTag
from aptos_sdk.account import Account

from modules.base import ModuleBase
from contracts.tokens.main import Tokens, TokenBase
from src import enums

if TYPE_CHECKING:
    from src.schemas.tasks.the_aptos_bridge import TheAptosBridgeClaimTask
    from src.schemas.wallet_data import WalletData


class AptosBridgeClaim(ModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'TheAptosBridgeClaimTask',
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

        self.task = task
        self.account = account
        self.available_tokens = Tokens().get_tokens_by_protocol(protocol=enums.ModuleName.THE_APTOS_BRIDGE)

    def get_unclaimed_amount_of_token_for_address(
            self,
            address: str,
            token_handle: str
    ) -> int:
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

    def get_all_unclaimed_tokens_for_address(self) -> list:
        unclaimed_token_objects = []

        for token in self.available_tokens:
            unclaimed_amount = self.get_unclaimed_amount_of_token_for_address(
                address=str(self.account.address()),
                token_handle=token.aptos_bridge_handle
            )
            if unclaimed_amount != 0:
                unclaimed_token_objects.append(token)

        return unclaimed_token_objects

    def build_transaction_payload(self, token_contract: TokenBase):
        payload = EntryFunction.natural(
            f"0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::coin_bridge",
            "claim_coin",
            [TypeTag(StructTag.from_str(token_contract.contract_address))],
            []
        )

        return payload

    def send_txn(self):
        tokens_to_claim = self.get_all_unclaimed_tokens_for_address()
        if not tokens_to_claim:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_status = self.module_execution_result
        for token in tokens_to_claim:
            txn_payload = self.build_transaction_payload(token_contract=token)
            if not txn_payload:
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
                self.module_execution_result.execution_info = f"Failed to build transaction payload"
                return self.module_execution_result

            txn_info_message = f"Claim bridged {token.name}."

            txn_status = self.simulate_and_send_transfer_type_transaction(
                account=self.account,
                txn_payload=txn_payload,
                txn_info_message=txn_info_message
            )

        return txn_status
