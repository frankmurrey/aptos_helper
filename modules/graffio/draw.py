import random
from typing import Union, TYPE_CHECKING

from aptos_sdk.transactions import EntryFunction, TransactionArgument
from aptos_sdk.bcs import Serializer
from aptos_sdk.account import Account, AccountAddress
from loguru import logger

from modules.base import ModuleBase
from modules.graffio.math import get_random_letter, get_random_coord
from src import enums
from src.schemas.canvas_config import CanvasConfig

if TYPE_CHECKING:
    from src.schemas.tasks import GraffioDrawTask

MAX_COLOR_INDEX = 7


class GraffioDraw(ModuleBase):
    router_address = "0x5d45bb2a6f391440ba10444c7734559bd5ef9053930e3ef53d05be332518522b"
    res_address = "0x915efe6647e0440f927d46e39bcb5eb040a7e567e1756e002073bc6e26f2cd23"

    def __init__(
            self,
            account: Account,
            task: 'GraffioDrawTask',
            base_url: str,
            proxies: dict = None
    ):
        super().__init__(
            task=task,
            base_url=base_url,
            proxies=proxies,
            account=account
        )

        self.account = account
        self.task = task

    def get_draw_resource(self) -> Union[None, dict]:
        try:
            res = self.client.account_resource(
                self.router_address,
                f"{self.res_address}::canvas_token::Canvas"
            )
            return res
        except Exception as ex:
            logger.error(f"Error while getting draw resource: {ex}")
            return None

    def build_transaction_payload(self):
        res = self.get_draw_resource()
        if res is None:
            return None

        config_dict = res['data']['config']
        config = CanvasConfig(**config_dict)

        inner = res['data']['mutator_ref']['self']

        if config.draw_enabled_for_non_admin is False:
            logger.error("Draw is disabled for non-admins")
            return None

        coords = get_random_coord(max_pixels=config.height)

        x_coords, y_coords = coords

        color = random.randint(0, MAX_COLOR_INDEX)

        seq_serializer = Serializer.sequence_serializer(Serializer.u16)
        seq_serializer_str = Serializer.sequence_serializer(Serializer.u8)

        transaction_args = [
            TransactionArgument(AccountAddress.from_hex(inner), Serializer.struct),
            TransactionArgument(x_coords, seq_serializer),
            TransactionArgument(y_coords, seq_serializer),
            TransactionArgument([color for _ in range(len(x_coords))], seq_serializer_str),
        ]

        payload = EntryFunction.natural(
            f"{self.res_address}::canvas_token",
            "draw",
            [],
            transaction_args
        )

        return payload

    def send_txn(self):
        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_status = self.simulate_and_send_transfer_type_transaction(
            account=self.account,
            txn_payload=txn_payload_data,
            txn_info_message="Pixel Draw"
        )

        return txn_status
