from typing import Callable, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from utils import validation
from src import enums


class TaskBase(BaseModel):
    """
    Task Base Schema

    Attributes:
        module_type: type of the task's module
        module_name: name of the task's module
        module: task's module

        task_id: id of the task
        task_status: status of the task execution

        probability: execution probability of the task

        result_hash: result hash of the task's transaction
        result_info: result info of the task

        forced_gas_limit: forced gas limit of the task's transaction
        max_fee: max fee of the task's transaction

        # TODO: Fill docs
    """
    class Config:
        extra = "allow"

    module_type: enums.ModuleType
    module_name: enums.ModuleName
    module: Optional[Callable]

    task_id: Union[UUID, str] = Field(default_factory=uuid4)
    task_status: enums.TaskStatus = enums.TaskStatus.CREATED

    probability: int = 100

    result_hash: Optional[str] = None
    result_info: Optional[str] = None

    forced_gas_limit: bool = False
    gas_limit: int
    gas_price: int

    # GLOBALS
    wait_for_receipt: bool = False
    txn_wait_timeout_sec: int = 60

    reverse_action: bool = False
    reverse_action_task: Optional[Callable] = None

    reverse_action_min_delay_sec: int = 1
    reverse_action_max_delay_sec: int = 2

    retries: int = 3

    min_delay_sec: float = 1
    max_delay_sec: float = 2

    test_mode: bool = True

    @property
    def action_info(self):
        return f""

    @validator("gas_limit", pre=True)
    def validate_gas_limit_pre(cls, value, values):
        value = validation.get_converted_to_int(value, "Max Fee")
        value = validation.get_positive(value, "Max Fee", include_zero=False)

        return value

    @validator("gas_price", pre=True)
    def validate_gas_price_pre(cls, value, values):
        value = validation.get_converted_to_int(value, "Gas Price")
        value = validation.get_positive(value, "Gas Price", include_zero=False)

        return value

    @validator("txn_wait_timeout_sec", pre=True)
    def validate_txn_wait_timeout_sec_pre(cls, value, values):

        if not values["wait_for_receipt"]:
            return 0

        value = validation.get_converted_to_float(value, "Txn Wait Timeout")
        value = validation.get_positive(value, "Txn Wait Timeout")

        return value

    @validator("min_delay_sec", pre=True)
    def validate_min_delay_sec_pre(cls, value):

        value = validation.get_converted_to_float(value, "Min Delay")
        value = validation.get_positive(value, "Min Delay")

        return value

    @validator("max_delay_sec", pre=True)
    def validate_max_delay_sec_pre(cls, value, values):

        value = validation.get_converted_to_float(value, "Max Delay")
        value = validation.get_greater(value, values["min_delay_sec"], "Max Delay")

        return value

    @validator("reverse_action_min_delay_sec", pre=True)
    def validate_reverse_action_min_delay_sec_pre(cls, value, values):
        if not values["reverse_action"]:
            return 0

        value = validation.get_converted_to_float(value, "Reverse Action Min Delay")
        value = validation.get_positive(value, "Reverse Action Min Delay")

        return value

    @validator("reverse_action_max_delay_sec", pre=True)
    def validate_reverse_action_max_delay_sec_pre(cls, value, values):
        if not values["reverse_action"]:
            return 0

        value = validation.get_converted_to_float(value, "Reverse Action Max Delay")
        value = validation.get_greater(value, values["reverse_action_min_delay_sec"], "Reverse Action Max Delay")

        return value

    @validator("retries", pre=True)
    def validate_retries_pre(cls, value):
        value = validation.get_converted_to_int(value, "Retries")
        value = validation.get_positive(value, "Retries")

        return value
