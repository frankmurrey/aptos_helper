import random
from typing import Union, TYPE_CHECKING

from aptos_sdk.transactions import EntryFunction, TransactionArgument, Serializer
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

import config
from modules.base import ModuleBase
from contracts.tokens.main import Tokens, TokenBase
from src import enums
from src.schemas.wallet_data import WalletData
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.action_models import TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks import TransferTask


class TokenTransfer(ModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'TransferTask',
            base_url: str,
            wallet_data: WalletData,
            proxies: dict = None,
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account,
            wallet_data=wallet_data
        )

        self.account = account
        self.task = task

        self.coin_x = Tokens().get_by_name(self.task.coin_x)

        self.recipient_address = wallet_data.pair_address

        if not self.coin_x:
            raise Exception(f"Coin {self.task.coin_x} not found")

        self.initial_balance_x_wei = self.get_wallet_token_balance(
            wallet_address=self.account.address(),
            token_address=self.coin_x.contract_address
        )
        self.token_x_decimals = self.get_token_decimals(self.coin_x)

    def calculate_amount_out_from_balance(
            self,
            coin_x: TokenBase,
    ) -> Union[int, None]:
        initial_balance_x_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals

        if initial_balance_x_decimals == 0:
            logger.error(f"Wallet {coin_x.symbol.upper()} balance is 0")
            return None

        if self.task.use_all_balance:
            amount_out_wei = self.initial_balance_x_wei

        elif self.task.send_percent_balance:
            percent = random.randint(
                int(self.task.min_amount_out), int(self.task.max_amount_out)
            ) / 100
            amount_out_wei = int(self.initial_balance_x_wei * percent)

        elif initial_balance_x_decimals < self.task.min_amount_out:
            logger.error(
                f"Wallet {coin_x.symbol.upper()} balance less than min amount out, "
                f"balance: {initial_balance_x_decimals}, min amount out: {self.task.min_amount_out}"
            )
            return None

        elif initial_balance_x_decimals < self.task.max_amount_out:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=initial_balance_x_decimals,
                decimals=self.token_x_decimals
            )

        else:
            amount_out_wei = self.get_random_amount_out_of_token(
                min_amount=self.task.min_amount_out,
                max_amount=self.task.max_amount_out,
                decimals=self.token_x_decimals
            )

        return amount_out_wei

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        if not self.recipient_address:
            logger.error("Recipient address is not set, please set it as wallet pair address")
            return None

        if len(self.recipient_address) != config.APTOS_KEY_LENGTH:
            logger.error(f"Recipient address is not valid, should be {config.APTOS_KEY_LENGTH} char long")
            return None

        address = self.get_address_from_hex(self.recipient_address)

        if self.coin_x.symbol.lower() != "aptos":
            is_coin_registered = self.is_token_registered_for_address(
                wallet_address=address,
                token_contract=self.coin_x.contract_address
            )
            if not is_coin_registered:
                logger.error(
                    f"Coin {self.coin_x.symbol.upper()} is not registered for recipient: {self.recipient_address}"
                )
                return None

        amount_out_wei = self.calculate_amount_out_from_balance(self.coin_x)
        if amount_out_wei is None:
            return None

        transaction_arguments = [
            TransactionArgument(address, Serializer.struct),
            TransactionArgument(int(amount_out_wei), Serializer.u64),
        ]

        if self.coin_x.symbol.lower() == "aptos":
            ty_args = []
            module = "0x1::aptos_account"
        else:
            ty_args = [TypeTag(StructTag.from_str(self.coin_x.contract_address))]
            module = "0x1::coin"

        payload = EntryFunction.natural(
            module,
            "transfer",
            ty_args,
            transaction_arguments,
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_out_wei / 10 ** self.token_x_decimals,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        payload = self.build_transaction_payload()
        if payload is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_info_message = (f"Transfer - {round(payload.amount_x_decimals, 4)} ({self.coin_x.symbol.upper()}), "
                            f"recipient: {self.recipient_address}.")

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=payload.payload,
            txn_info_message=txn_info_message
        )

        return txn_status




