from typing import Callable
from pydantic import Field

from src import enums

from src.schemas.tasks import TradeTaskBase
from src.schemas.tasks import WithdrawTaskBase
from src.schemas import validation_mixins

from modules.gator.trade import GatorTrade
from modules.gator.deposit import GatorDeposit
from modules.gator.withdraw import GatorWithdraw


class GatorTradeTask(
    TradeTaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.GATOR
    module_type: enums.ModuleType = enums.ModuleType.TRADE
    module: Callable = Field(default=GatorTrade)


class GatorDepositTask(
    validation_mixins.MinMaxAmountOutValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.GATOR
    module_type: enums.ModuleType = enums.ModuleType.DEPOSIT
    module: Callable = Field(default=GatorDeposit)

    coin_x: str

    min_amount_out: float
    max_amount_out: float


class GatorWithdrawTask(WithdrawTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.GATOR
    module_type: enums.ModuleType = enums.ModuleType.WITHDRAW
    module: Callable = Field(default=GatorWithdraw)
