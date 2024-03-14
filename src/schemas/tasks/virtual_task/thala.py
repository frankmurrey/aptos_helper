from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import ThalaSwapTask, ThalaRemoveLiquidityTask, ThalaAddLiquidityTask
from src.schemas.tasks import ThalaWithdrawTask, ThalaSupplyTask


class ThalaSwapVirtualTask(
    ThalaSwapTask,
    VirtualTaskBase,
):
    pass


class ThalaRemoveLiquidityVirtualTask(
    ThalaRemoveLiquidityTask,
    VirtualTaskBase,
):
    pass


class ThalaAddLiquidityVirtualTask(
    ThalaAddLiquidityTask,
    VirtualTaskBase,
):
    pass


class ThalaWithdrawVirtualTask(
    ThalaWithdrawTask,
    VirtualTaskBase,
):
    pass


class ThalaSupplVirtualTask(
    ThalaSupplyTask,
    VirtualTaskBase,
):
    pass
