from src.schemas.tasks.virtual_task.base import VirtualTaskBase
from src.schemas.tasks import LiquidSwapSwapTask, LiquidSwapRemoveLiquidityTask, LiquidSwapAddLiquidityTask


class LiquidSwapSwapVirtualTask(
    VirtualTaskBase,
    LiquidSwapSwapTask
):
    pass


class LiquidSwapRemoveLiquidityVirtualTask(
    VirtualTaskBase,
    LiquidSwapRemoveLiquidityTask
):
    pass


class LiquidSwapAddLiquidityVirtualTask(
    VirtualTaskBase,
    LiquidSwapAddLiquidityTask
):
    pass
