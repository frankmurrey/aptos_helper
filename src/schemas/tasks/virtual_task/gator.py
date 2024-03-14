from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import GatorDepositTask, GatorWithdrawTask, GatorTradeTask


class GatorTradeVirtualTask(
    VirtualTaskBase,
    GatorTradeTask
):
    pass


class GatorDepositVirtualTask(
    VirtualTaskBase,
    GatorDepositTask
):
    pass


class GatorWithdrawVirtualTask(
    VirtualTaskBase,
    GatorWithdrawTask
):
    pass
