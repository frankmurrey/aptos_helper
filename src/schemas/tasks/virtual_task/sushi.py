from typing import Callable
from pydantic import Field

from src.schemas.tasks.base.swap import SwapTaskBase
from modules.sushi.swap import SushiSwap
from src import enums


class SushiSwapTask(SwapTaskBase):
    module_name: enums.ModuleName = enums.ModuleName.SUSHI
    module_type: enums.ModuleType = enums.ModuleType.SWAP
    module: Callable = Field(default=SushiSwap)

