from typing import Callable, Optional
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.liquid_swap.swap import LiquidSwapSwap
from modules.liquid_swap.liquidity import LiquidSwapAddLiquidity
from modules.liquid_swap.liquidity import LiquidSwapRemoveLiquidity
from src import enums


class LiquidSwapSwapReverseTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.LIQUID_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=LiquidSwapSwap)


class LiquidSwapSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.LIQUID_SWAP
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=LiquidSwapSwap)
    reverse_action_task: Optional[Callable] = Field(default=LiquidSwapSwapReverseTask)

    class Config:
        arbitrary_types_allowed = True


class LiquidSwapRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name = enums.ModuleName.LIQUID_SWAP
    module_type = enums.ModuleType.LIQUIDITY_REMOVE
    module: Optional[Callable] = Field(default=LiquidSwapRemoveLiquidity)


class LiquidSwapAddLiquidityTask(AddLiquidityTaskBase):
    module_name = enums.ModuleName.LIQUID_SWAP
    module_type = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=LiquidSwapAddLiquidity)
    reverse_action_task = Field(default=LiquidSwapRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True

