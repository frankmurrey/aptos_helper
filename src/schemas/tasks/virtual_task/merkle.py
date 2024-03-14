from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import MerklePlaceOpenOrderTask, MerklePlaceCancelOrderTask


class MerklePlaceCancelOrderVirtualTask(
    VirtualTaskBase,
    MerklePlaceCancelOrderTask
):
    pass


class MerklePlaceOpenOrderVirtualTask(
    VirtualTaskBase,
    MerklePlaceOpenOrderTask
):
    pass
