from typing import Callable
from pydantic import Field

from src import enums
from src.schemas import validation_mixins
from src.schemas.tasks.base.base import TaskBase
from modules.transfer.token_transfer import TokenTransfer


class TransferTask(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    module_name = enums.ModuleName.TOKEN
    module_type = enums.ModuleType.TRANSFER
    module = Field(default=TokenTransfer)

    coin_x: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    min_amount_out: float
    max_amount_out: float

    @property
    def action_info(self):
        info = f"{self.coin_x.upper()}"

        return info
