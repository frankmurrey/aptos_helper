from typing import Optional, Callable
from pydantic import Field
from modules.random.swap import RandomSwap


from src import enums
from src.schemas.tasks.base.swap import SwapTaskBase


class RandomSwapTask(SwapTaskBase):
    module_name = enums.ModuleName.RANDOM
    module_type = enums.ModuleType.SWAP
    module = Field(default=RandomSwap)
