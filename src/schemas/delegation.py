from src.schemas.base import TransferBase


class DelegateConfigSchema(TransferBase):
    module_name: str = "delegate"
    validator_addr: str = ""


class UnlockConfigSchema(TransferBase):
    module_name: str = "unlock"
    validator_addr: str = ""