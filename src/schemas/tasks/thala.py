from typing import Callable, Optional
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from src.schemas.tasks.base.supply import SupplyTaskBase
from src.schemas.tasks.base.withdraw import WithdrawTaskBase
from modules.thala.swap import ThalaSwap
from modules.thala.liquidity import ThalaAddLiquidity
from modules.thala.liquidity import ThalaRemoveLiquidity
from modules.thala.supply import ThalaSupply
from modules.thala.supply import ThalaWithdraw

from src import enums


class ThalaSwapReverseTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.THALA
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=ThalaSwap)


class ThalaSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.THALA
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=ThalaSwapReverseTask)
    reverse_action_task: Optional[Callable] = Field(default=ThalaSwapReverseTask)

    class Config:
        arbitrary_types_allowed = True


class ThalaRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=ThalaRemoveLiquidity)


class ThalaAddLiquidityTask(AddLiquidityTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=ThalaAddLiquidity)
    reverse_action_task: Optional[Callable] = Field(default=ThalaRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True


class ThalaWithdrawTask(WithdrawTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.WITHDRAW
    module: Callable = Field(default=ThalaWithdraw)

    class Config:
        arbitrary_types_allowed = True


class ThalaSupplyTask(SupplyTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.SUPPLY
    module: Callable = Field(default=ThalaSupply)
    reverse_action_task: Callable = Field(default=ThalaWithdrawTask)

    class Config:
        arbitrary_types_allowed = True
