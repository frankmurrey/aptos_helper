from typing import Optional

from pydantic import BaseModel
from pydantic import validator

from src.exceptions import AppValidationError
from utils import validation


class MinMaxAmountOutValidationMixin(BaseModel):

    use_all_balance: Optional[bool] = False

    min_amount_out_range: Optional[tuple]
    max_amount_out_range: Optional[tuple]

    min_amount_out: float
    max_amount_out: float

    @validator("min_amount_out", pre=True, check_fields=False)
    def validate_min_amount_out_pre(cls, value, values):

        if "use_all_balance" in values:
            if values["use_all_balance"]:
                return 0

        value = validation.get_converted_to_float(value, "Min Amount Out")

        range_value: tuple = values.get("min_amount_out_range")
        if range_value is not None:
            if range_value[0] is not None:
                value = validation.get_greater(value, range_value[0], "Min Amount Out")

            if range_value[1] is not None:
                value = validation.get_lower(value, range_value[1], "Min Amount Out")

        else:
            value = validation.get_positive(value, "Min Amount Out", include_zero=False)

        return value

    @validator("max_amount_out", pre=True, check_fields=False)
    def validate_max_amount_out_pre(cls, value, values):

        if "use_all_balance" in values:
            if values["use_all_balance"]:
                return 0

        if "min_amount_out" not in values:
            raise AppValidationError("Min Amount Out is required")

        value = validation.get_converted_to_float(value, "Max Amount Out")

        range_value: tuple = values.get("max_amount_out_range")
        if range_value is not None:
            if range_value[0] is not None:
                value = validation.get_greater(value, range_value[0], "Max Amount Out")

            if range_value[1] is not None:
                value = validation.get_lower(value, range_value[1], "Max Amount Out")

        else:
            value = validation.get_positive(value, "Max Amount Out", include_zero=False)

        value = validation.get_greater(value, values["min_amount_out"], "Max Amount Out")

        return value
