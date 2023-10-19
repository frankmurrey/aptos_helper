from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from modules.thala.liquidity import ThalaAddLiquidity
from modules.thala.liquidity import ThalaRemoveLiquidity

from src import enums


class ThalaRemoveLiquidityTask(RemoveLiquidityTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.LIQUIDITY_REMOVE
    module: Callable = Field(default=ThalaRemoveLiquidity)


class ThalaAddLiquidityTask(AddLiquidityTaskBase):
    module_name = enums.ModuleName.THALA
    module_type = enums.ModuleType.LIQUIDITY_ADD
    module: Callable = Field(default=ThalaAddLiquidity)
    reverse_action_task: Callable = Field(default=ThalaRemoveLiquidityTask)

    class Config:
        arbitrary_types_allowed = True

