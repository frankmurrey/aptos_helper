from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.supply import SupplyTaskBase
from src.schemas.tasks.base.withdraw import WithdrawTaskBase
from modules.abel.mint import AbleFinanceMint
from modules.abel.redeem import AbleFinanceRedeem

from src import enums


class AbelWithdrawTask(WithdrawTaskBase):
    module_name = enums.ModuleName.ABEL
    module_type = enums.ModuleType.WITHDRAW
    module: Callable = Field(default=AbleFinanceRedeem)


class AbelSupplyTask(SupplyTaskBase):
    module_name = enums.ModuleName.ABEL
    module_type = enums.ModuleType.SUPPLY
    module: Callable = Field(default=AbleFinanceMint)
    reverse_action_task = Field(default=AbelWithdrawTask)

    class Config:
        arbitrary_types_allowed = True


