from src.schemas.tasks import WithdrawTaskBase, SupplyTaskBase
from src.schemas.tasks.virtual_task.base import VirtualTaskBase


class AbelWithdrawVirtualTask(
    WithdrawTaskBase,
    VirtualTaskBase,
):
    pass


class AbelSupplyVirtualTask(
    SupplyTaskBase,
    VirtualTaskBase,
):
    pass
