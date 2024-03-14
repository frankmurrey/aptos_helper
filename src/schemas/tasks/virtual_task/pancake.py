from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import PancakeSwapTask


class PancakeSwapVirtualTask(
    PancakeSwapTask,
    VirtualTaskBase,
):
    pass
