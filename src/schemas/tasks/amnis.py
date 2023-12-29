from typing import Callable
from pydantic import Field

from src import enums
from src.schemas.tasks import TaskBase
from src.schemas.tasks import WithdrawTaskBase
from src.schemas import validation_mixins

from modules.amnis.stake import AmnisMintAndStake
from modules.amnis.unstake import AmnisUnstake


class AmnisMintAndStakeTask(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.AMNIS
    module_type: enums.ModuleType = enums.ModuleType.MINT
    module: Callable = Field(default=AmnisMintAndStake)

    coin_x: str = "aptos"

    min_amount_out = 0.2
    max_amount_out = 0.2


class AmnisUnstakeTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.AMNIS
    module_type: enums.ModuleType = enums.ModuleType.UNSTAKE
    module: Callable = Field(default=AmnisUnstake)
