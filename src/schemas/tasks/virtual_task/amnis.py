from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import AmnisMintAndStakeTask, AmnisUnstakeTask


class AmnisMintAndStakeVirtualTask(
    VirtualTaskBase,
    AmnisMintAndStakeTask
):
    pass


class AmnisUnstakeVirtualTask(
    VirtualTaskBase,
    AmnisUnstakeTask
):
    pass
