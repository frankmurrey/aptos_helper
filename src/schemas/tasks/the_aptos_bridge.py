from typing import Callable
from pydantic import Field

from src import enums
from src.schemas.tasks.base.bridge import BridgeTaskBase
from src.schemas.tasks.base.base import TaskBase
from modules.the_aptos_bridge.bridge import AptosBridge
from modules.the_aptos_bridge.claim import AptosBridgeClaim


class TheAptosBridgeTask(BridgeTaskBase):
    module_name = enums.ModuleName.THE_APTOS_BRIDGE
    module_type = enums.ModuleType.BRIDGE
    module = Field(default=AptosBridge)


class TheAptosBridgeClaimTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.THE_APTOS_BRIDGE
    module_type: enums.ModuleType = enums.ModuleType.CLAIM
    module: Callable = Field(default=AptosBridgeClaim)
