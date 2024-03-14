from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from modules.pancake.swap import PancakeSwap
from src import enums


class PancakeSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.PANCAKE
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=PancakeSwap)
