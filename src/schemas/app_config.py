from pydantic import BaseModel
from pydantic import validator

from src import exceptions
from src import enums
from utils import validation


class AppConfigSchema(BaseModel):
    run_mode: enums.RunMode = enums.RunMode.SYNC
    preserve_logs: bool = True
    use_proxy: bool = True
    rpc_url: str = "https://rpc.ankr.com/http/aptos/v1"
    wallets_amount_to_execute_in_test_mode: int = 3

    debug: bool = False

    @validator('rpc_url', pre=True)
    def rpc_url_must_be_valid(cls, value):
        if not value:
            raise exceptions.AppValidationError("RPC URL can't be empty")

        return value

    @validator('wallets_amount_to_execute_in_test_mode', pre=True)
    def wallets_amount_to_execute_in_test_mode_must_be_valid(cls, value):
        value = validation.get_converted_to_int(value, "Wallets amount")
        value = validation.get_positive(value, "Wallets amount", include_zero=False)

        return value
