from typing import Union

from pydantic import BaseModel


class BalanceCheckerConfigSchema(BaseModel):
    module_name: str = "balance_checker"
    coin_option: str = ""
    min_delay_sec: Union[int, str] = 1
    max_delay_sec: Union[int, str] = 1
    file_path: str = ""
    test_mode: bool = False