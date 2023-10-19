from typing import Union

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase


class RemoveLiquidityTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    coin_x: str
    coin_y: str
    slippage: float = 0.5

    @property
    def action_info(self):
        return f"{self.coin_x.upper()} + {self.coin_y.upper()}"


