import binascii
import random
from typing import Union, TYPE_CHECKING

from aptos_sdk.transactions import EntryFunction, TransactionArgument, Serializer
from loguru import logger

import config
from modules.base import ModuleBase
from contracts.tokens.main import Tokens
from contracts.chains.main import Chains
from src import enums
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.action_models import TransactionPayloadData
from src.schemas.wallet_data import WalletData
from modules.the_aptos_bridge.src_lz.executor import Executor
from modules.the_aptos_bridge.src_lz.endpoint import Endpoint

from aptos_sdk.type_tag import TypeTag, StructTag
from aptos_sdk.account import Account, AccountAddress

if TYPE_CHECKING:
    from src.schemas.tasks import TheAptosBridgeTask


class AptosBridge(ModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'TheAptosBridgeTask',
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

        self.task = task
        self.account = account
        self.receiver_address = wallet_data.pair_address

        self.router_address = self.get_address_from_hex(
            "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa"
        )

    def get_lz_fee(
            self,
            dst_chain_id: int,
            adapter_params
    ) -> int:
        endpoint = Endpoint(self.client)

        fee = endpoint.quote_fee(
            ua_address=self.router_address,
            dst_chain_id=dst_chain_id,
            adapter_params=adapter_params,
            payload_size=74
        )
        return int(fee)

    def build_txn_payload_data(self) -> Union[TransactionPayloadData, None]:
        if not self.receiver_address or len(self.receiver_address) != config.EVM_ADDRESS_LENGTH:
            logger.error(f"Receiver (Pair address) address is invalid,"
                         f" should be {config.EVM_ADDRESS_LENGTH} char length")
            return None

        coin_to_bridge = Tokens().get_by_name(name_query=self.task.coin_x)
        dst_chain = Chains().get_by_name(name_query=self.task.dst_chain_name)
        recipient_address = AccountAddress.from_hex(self.receiver_address)
        wallet_apt_balance = self.get_wallet_aptos_balance(wallet_address=self.account.address())

        if wallet_apt_balance == 0:
            logger.error("Wallet Aptos balance is 0")
            return None

        if not coin_to_bridge or not dst_chain:
            logger.error("Coin to bridge or destination chain not found")
            return None

        executor = Executor(self.client)
        adapter_params = executor.get_default_adapter_params(dst_chain_id=dst_chain.id)

        fee = self.get_lz_fee(
            dst_chain_id=dst_chain.id,
            adapter_params=adapter_params
        )
        if not fee:
            logger.error("Fee calculation failed")
            return None

        if fee > int(wallet_apt_balance):
            logger.error("Not enough aptos balance for fee")
            return None

        wallet_token_balance = self.get_wallet_token_balance(
            wallet_address=self.account.address(),
            token_address=coin_to_bridge.contract_address
        )

        if wallet_token_balance == 0:
            logger.error(f"Wallet token {coin_to_bridge.symbol.upper()} balance is 0")
            return None

        wallet_token_balance_decimals = wallet_token_balance * 10 ** self.get_token_decimals(
            token_obj=coin_to_bridge)

        coin_x_decimals = self.get_token_decimals(token_obj=coin_to_bridge)
        if self.task.use_all_balance:
            amount_out = wallet_token_balance

        elif wallet_token_balance_decimals < self.task.max_amount_out:
            amount_out = random.randint(
                self.task.min_amount_out * 10 ** coin_x_decimals,
                wallet_token_balance_decimals
            )

        else:
            amount_out = random.randint(
                self.task.min_amount_out * 10 ** coin_x_decimals,
                self.task.max_amount_out * 10 ** coin_x_decimals
            )
        if wallet_token_balance < amount_out:
            logger.error(f"Wallet token {coin_to_bridge.symbol.upper()} balance is less than amount out")
            return

        transaction_args = [
            TransactionArgument(
                int(dst_chain.id),
                Serializer.u64
            ),
            TransactionArgument(
                list(binascii.unhexlify(str(recipient_address)[2:])),
                Serializer.sequence_serializer(Serializer.u8)
            ),
            TransactionArgument(
                int(amount_out),
                Serializer.u64
            ),
            TransactionArgument(
                int(fee),
                Serializer.u64
            ),
            TransactionArgument(
                0,
                Serializer.u64
            ),
            TransactionArgument(
                False,
                Serializer.bool
            ),
            TransactionArgument(
                list(binascii.unhexlify(adapter_params[2:])),
                Serializer.sequence_serializer(Serializer.u8)
            ),
            TransactionArgument(
                [],
                Serializer.sequence_serializer(Serializer.u8)
            ),
        ]

        payload = EntryFunction.natural(
            f"{self.router_address}::coin_bridge",
            "send_coin_from",
            [
                TypeTag(StructTag.from_str(coin_to_bridge.contract_address))
            ],
            transaction_args
        )
        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out / 10 ** coin_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        txn_payload_data = self.build_txn_payload_data()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = f"{txn_payload_data.amount_x_decimals} {self.task.coin_x.upper()}" \
                           f" bridge to {self.task.dst_chain_name.upper()}, receiver: {self.receiver_address}."

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data.payload,
            txn_info_message=txn_info_message
        )

        return txn_status
