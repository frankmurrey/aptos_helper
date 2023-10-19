from pydantic import validator

from src.schemas.tasks.base.base import TaskBase
from src.schemas import validation_mixins


class TransferTaskBase(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    coin_x: str

    min_amount_out: float
    max_amount_out: float

    use_all_balance: bool = False
    send_percent_balance: bool = False

    @property
    def action_info(self):
        return f"{self.coin_x.upper()}"
