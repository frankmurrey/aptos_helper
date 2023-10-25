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
