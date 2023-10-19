from src.schemas.tasks.base import TaskBase


class MintTaskBase(
    TaskBase,
):
    coin_x: str

    @property
    def action_info(self):
        if self.reverse_action:
            return f"{self.coin_x.upper()}"
        else:
            return f"{self.coin_x.upper()}"
