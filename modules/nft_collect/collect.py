import random
import time
import json
from typing import Union, TYPE_CHECKING, List

from aptos_sdk.transactions import EntryFunction, TransactionArgument, Serializer
from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

import config
from modules.base import ModuleBase
from modules.nft_collect import data
from src import enums
from src.schemas.wallet_data import WalletData
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.action_models import TransactionPayloadData

if TYPE_CHECKING:
    from src.schemas.tasks.nft_collect import NftCollectTask


class NftCollect(ModuleBase):
    def __init__(
            self,
            account: Account,
            task: 'NftCollectTask',
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

        self.recipient_address = wallet_data.pair_address

    def get_all_collectibles_data_for_wallet(
            self,
            wallet_address: AccountAddress
    ) -> Union[List[dict], None]:
        """
        Fetches first 20 collectibles owned by wallet
        :param wallet_address:
        :return:
        """
        try:
            url = f"https://indexer.mainnet.aptoslabs.com/v1/graphql/"
            payload = {
                "query": data.query,
                "variables": data.get_vars(str(wallet_address))
            }

            response = self.client.client.post(
                url=url,
                json=payload
            )
            if not response.is_success:
                logger.error(f"Failed while getting collectibles list for wallet")
                return None

            bytes_data = response.read()
            string_data = bytes_data.decode('utf-8')
            data_dict = json.loads(string_data)

            tokens_data: list = data_dict['data']['current_token_ownerships_v2']

            return tokens_data

        except Exception as e:
            logger.error(f"Error while getting pools data: {e}")
            return None

    def get_v2_collectibles_for_wallet(
            self,
            wallet_address: AccountAddress
    ) -> Union[List[dict], None]:
        """
        Fetches first 20 collectibles owned by wallet
        :param wallet_address:
        :return:
        """
        try:
            all_collectibles = self.get_all_collectibles_data_for_wallet(wallet_address)
            if all_collectibles is None:
                return None

            v2_collectibles = []
            for collectible in all_collectibles:
                if collectible['token_standard'] == "v2":
                    v2_collectibles.append(collectible)

            return v2_collectibles

        except Exception as e:
            logger.error(f"Error while getting pools data: {e}")
            return None

    def build_transaction_payload(
            self,
            token_address: str
    ) -> Union[TransactionPayloadData, None]:
        if not self.recipient_address:
            logger.error("Recipient address is not set, please set it as wallet pair address")
            return None

        if len(self.recipient_address) != config.APTOS_KEY_LENGTH:
            logger.error(f"Recipient address is not valid, should be {config.APTOS_KEY_LENGTH} char long")
            return None

        address = self.get_address_from_hex(self.recipient_address)
        token_address = AccountAddress.from_hex(token_address)

        transaction_arguments = [
            TransactionArgument(token_address, Serializer.struct),
            TransactionArgument(address, Serializer.struct),
        ]

        payload = EntryFunction.natural(
            "0x1::object",
            "transfer",
            [TypeTag(StructTag.from_str("0x4::token::Token"))],
            transaction_arguments
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=0,
            amount_y_decimals=0
        )

    def send_txn(self) -> ModuleExecutionResult:
        all_v2_collectibles = self.get_v2_collectibles_for_wallet(wallet_address=self.account.address())
        if all_v2_collectibles is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while getting collectibles list"
            return self.module_execution_result

        logger.info(f"Found ({len(all_v2_collectibles)}) V2 NFT's in wallet")
        for index, collectible in enumerate(all_v2_collectibles):
            token_address = collectible.get('token_data_id')
            if token_address is None:
                logger.error(f"{index + 1} NFT address is not found in collectible: {collectible}")
                continue

            payload = self.build_transaction_payload(token_address)
            if payload is None:
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
                self.module_execution_result.execution_info = "Error while building transaction payload"
                return self.module_execution_result

            txn_info_message = (f"NFT V2 collect - Transferring {index + 1}/{len(all_v2_collectibles)} NFT, "
                                f"recipient: {self.recipient_address}.")

            txn_status = self.simulate_and_send_transfer_type_transaction(
                account=self.account,
                txn_payload=payload.payload,
                txn_info_message=txn_info_message
            )

            if txn_status.execution_status == enums.ModuleExecutionStatus.ERROR:
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
                self.module_execution_result.execution_info = txn_status.execution_info
                return txn_status

            if index + 1 == len(all_v2_collectibles):
                self.module_execution_result.execution_status = enums.ModuleExecutionStatus.SUCCESS
                self.module_execution_result.execution_info = "Successfully transferred all NFT's"
                return self.module_execution_result

            delay = random.uniform(self.task.min_delay_nft_transfer_sec, self.task.max_delay_nft_transfer_sec)
            logger.info(f"Sleeping for {int(delay)} seconds")
            time.sleep(int(delay))

        self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
        self.module_execution_result.execution_info = "No collectibles found"
        return self.module_execution_result
