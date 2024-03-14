from typing import Callable
from pydantic import Field
from pydantic import validator

import config
from src import enums
from src.schemas import validation_mixins
from src.schemas.tasks.base.base import TaskBase
from modules.delegation.delegate import Delegate
from modules.delegation.unlock import Unlock
from src.exceptions import AppValidationError


class DelegateTask(
    TaskBase,
    validation_mixins.MinMaxAmountOutValidationMixin
):
    module_name: enums.ModuleName = enums.ModuleName.GRAFFIO
    module_type: enums.ModuleType = enums.ModuleType.DELEGATE
    min_amount_out: int
    max_amount_out: int
    validator_address: str = ""
    module: Callable = Field(default=Delegate)

    @validator("validator_address", pre=True)
    def validate_validator_address(cls, v):
        if len(v) != config.APTOS_KEY_LENGTH:
            print(len(v))
            raise AppValidationError(f"Invalid validator address, should be {config.APTOS_KEY_LENGTH} characters long")

        return v

    @validator("min_amount_out", pre=True)
    def validate_min_amount_out(cls, v):
        if v < 11:
            raise AppValidationError("Minimum delegation amount must be >= 11")

        return v


class UnlockTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.UNLOCK
    module_type: enums.ModuleType = enums.ModuleType.UNLOCK
    module: Callable = Field(default=Unlock)
    validator_address: str = ""

    @validator("validator_address", pre=True)
    def validate_validator_address(cls, v):
        if len(v) != config.APTOS_KEY_LENGTH:
            raise AppValidationError(f"Invalid validator address, should be {config.APTOS_KEY_LENGTH} characters long")

        return v