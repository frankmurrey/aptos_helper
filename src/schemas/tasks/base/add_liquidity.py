import random
from pydantic import validator

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase
from src.exceptions import AppValidationError
from utils import validation
from contracts.tokens.main import Tokens
from src import enums


class AddLiquidityTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.SameCoinValidationMixin
):
    random_y_coin: bool = False

    coin_x: str
    coin_y: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    min_amount_out: float = 0
    max_amount_out: float = 0

    slippage: float = 2

    def __init__(self, **data):
        super().__init__(**data)

        if self.random_y_coin:
            if self.module_name == enums.ModuleName.RANDOM:
                self.coin_y = enums.MiscTypes.RANDOM
            else:
                protocol_coins_obj = Tokens().get_tokens_by_protocol(self.module_name)
                protocol_coins = [coin.symbol for coin in protocol_coins_obj]
                protocol_coins.remove(self.coin_x.lower())
                self.coin_y = random.choice(protocol_coins)

    @property
    def action_info(self):
        coin_y = "Rand" if self.random_y_coin else self.coin_y.upper()
        symbol = "+" if not self.reverse_action else "+-"
        return f"{self.coin_x.upper()} {symbol} {coin_y}"

    @validator("min_amount_out", pre=True)
    def validate_min_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        value = validation.get_converted_to_float(value, "Min Amount Out")
        value = validation.get_positive(value, "Min Amount Out", include_zero=False)

        return value

    @validator("max_amount_out", pre=True)
    def validate_max_amount_out_pre(cls, value, values):

        if values["use_all_balance"]:
            return 0

        if "min_amount_out" not in values:
            raise AppValidationError("Min Amount Out is required")

        value = validation.get_converted_to_float(value, "Max Amount Out")
        value = validation.get_positive(value, "Max Amount Out", include_zero=False)
        value = validation.get_greater(value, values["min_amount_out"], "Max Amount Out")

        return value
