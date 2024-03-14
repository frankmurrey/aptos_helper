from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import SushiSwapTask


class SushiSwapVirtualTask(
    SushiSwapTask,
    VirtualTaskBase,
):
    pass
