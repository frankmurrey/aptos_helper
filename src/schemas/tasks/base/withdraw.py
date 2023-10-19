from typing import Union

from src.schemas.tasks.base import TaskBase


class WithdrawTaskBase(TaskBase):
    coin_x: Union[str]

    @property
    def action_info(self):
        return f"{self.coin_x.upper()}"
