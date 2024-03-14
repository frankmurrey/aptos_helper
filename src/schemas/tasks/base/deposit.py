from typing import Union

from src.schemas.tasks.base import TaskBase
from src.schemas import validation_mixins


class DepositTaskBase(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin
):
    coin_x: Union[str]

    min_amount_out: float
    max_amount_out: float

    @property
    def action_info(self):
        return f"{self.coin_x.upper()}"
