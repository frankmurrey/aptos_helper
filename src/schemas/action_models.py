from typing import Optional, Callable

from pydantic import BaseModel
from aptos_sdk.transactions import EntryFunction
from pydantic import Field

from src import enums


class ModuleExecutionResult(BaseModel):
    # TODO remake retry_needed
    execution_status: enums.ModuleExecutionStatus = enums.ModuleExecutionStatus.FAILED
    retry_needed: bool = True
    execution_info: Optional[str] = ""
    hash: Optional[str] = ""


class TransactionSimulationResult(BaseModel):
    result: enums.TransactionStatus
    vm_status: Optional[str] = None
    gas_used: int


class TransactionReceipt(BaseModel):
    status: enums.TransactionStatus
    vm_status: Optional[str] = None


class TransactionPayloadData(BaseModel):
    payload: EntryFunction
    amount_x_decimals: float
    amount_y_decimals: float

    class Config:
        arbitrary_types_allowed = True
