import time
from typing import Union

from aptos_sdk.account import Account
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from loguru import logger

from src.schemas.tasks.base.swap import SwapTaskBase
from utils.delay import get_delay
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from src import enums
from src.schemas.wallet_data import WalletData


from modules.base import ModuleBase


class ThalaDeposit(ModuleBase):
    def __init__(
            self,
            account: Account,
            task: SwapTaskBase,
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies,
            wallet_data=wallet_data
        )
