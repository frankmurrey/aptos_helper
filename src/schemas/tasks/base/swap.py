import random

from pydantic import validator

from src.schemas import validation_mixins
from src.schemas.tasks.base import TaskBase
from src.exceptions import AppValidationError
from contracts.tokens.main import Tokens
from utils import validation
from src import enums


class SwapTaskBase(
    TaskBase,
    validation_mixins.SlippageValidationMixin,
    validation_mixins.MinMaxAmountOutValidationMixin,
):
    random_y_coin: bool = False

    coin_x: str
    coin_y: str

    use_all_balance: bool = False
    send_percent_balance: bool = False

    compare_with_cg_price: bool = True

    min_amount_out: float
    max_amount_out: float

    max_price_difference_percent: float = 2

    slippage: float = 0.5

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
        symbol = "->" if not self.reverse_action else "<->"

        info = f"{self.coin_x.upper()} {symbol} {coin_y}"

        return info

    @validator("coin_y", pre=True)
    def validate_coin_to_receive_pre(cls, value, values):
        if values["random_y_coin"]:
            return value

        if value == values["coin_x"]:
            raise AppValidationError("Coin to receive cannot be the same as Coin to swap")

        return value

    @validator("max_price_difference_percent", pre=True)
    def validate_max_price_difference_percent_pre(cls, value, values):

        if not values["compare_with_cg_price"]:
            return 0

        value = validation.get_converted_to_float(value, "Max Price Difference Percent")
        value = validation.get_positive(value, "Max Price Difference Percent", include_zero=True)
        value = validation.get_lower(value, 100, "Max Price Difference Percent", include_max=False)

        return value

