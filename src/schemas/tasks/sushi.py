from typing import Callable, Optional
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from modules.sushi.swap import SushiSwap
from src import enums


class SushiSwapReverseTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SUSHI
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=SushiSwap)


class SushiSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SUSHI
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=SushiSwapReverseTask)
    reverse_action_task: Optional[Callable] = Field(default=SushiSwapReverseTask)

    class Config:
        arbitrary_types_allowed = True
