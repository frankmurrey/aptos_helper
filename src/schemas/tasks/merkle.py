from typing import Callable
from pydantic import Field

from src import enums

from src.schemas.tasks.base.base import TaskBase
from src.schemas import validation_mixins
from modules.merkle.place_order import MerklePlaceOrder


class MerklePlaceOrderTask(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin,
    validation_mixins.SlippageValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.MERKLE
    module_type: enums.ModuleType = enums.ModuleType.PLACE_ORDER
    module: Callable = Field(default=MerklePlaceOrder)
    reverse_action_task: Callable = Field(default=None)

    coin_x: str = "usdc"

    slippage: float = 0.5

    min_amount_out: float = 2
    max_amount_out: float = 2
    use_referral: bool = False

    order_type: enums.OrderType = enums.OrderType.LONG

    class Config:
        arbitrary_types_allowed = True
