from typing import Callable
from pydantic import Field
from pydantic import validator

from src import enums

from src.schemas.tasks.base.base import TaskBase
from src.schemas import validation_mixins
from src.exceptions import AppValidationError
from modules.merkle.place_order import MerklePlaceOpenOrder
from modules.merkle.place_order import MerklePlaceCancelOrder


class MerklePlaceCancelOrderTask(
    TaskBase,
    validation_mixins.SlippageValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.MERKLE
    module_type: enums.ModuleType = enums.ModuleType.PLACE_CANCEL_ORDER
    module: Callable = Field(default=MerklePlaceCancelOrder)

    coin_x: str = "usdc"

    slippage: float = 0.5
    use_referral: bool = False

    order_type: enums.OrderType = enums.OrderType.LONG


class MerklePlaceOpenOrderTask(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
    validation_mixins.SlippageValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.MERKLE
    module_type: enums.ModuleType = enums.ModuleType.PLACE_OPEN_ORDER
    module: Callable = Field(default=MerklePlaceOpenOrder)
    reverse_action_task: Callable = Field(default=MerklePlaceCancelOrderTask)

    coin_x: str = "usdc"

    slippage: float = 0.5

    min_amount_out_range = (2, None)

    min_amount_out: float = 2
    max_amount_out: float = 2

    pseudo_order: bool = False
    use_referral: bool = False

    order_type: enums.OrderType = enums.OrderType.LONG

    class Config:
        arbitrary_types_allowed = True

    @property
    def action_info(self):
        return self.order_type.value.title()
