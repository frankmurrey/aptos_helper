from typing import Callable, Optional
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from modules.pancake.swap import PancakeSwap
from src import enums


class PancakeSwapReverseTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.PANCAKE
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=PancakeSwap)


class PancakeSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.PANCAKE
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=PancakeSwap)
    reverse_action_task: Optional[Callable] = Field(default=PancakeSwapReverseTask)

    class Config:
        arbitrary_types_allowed = True
