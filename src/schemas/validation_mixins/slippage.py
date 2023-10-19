from pydantic import BaseModel
from pydantic import validator

from utils import validation


class SlippageValidationMixin(BaseModel):

    slippage: float

    @validator("slippage", pre=True, check_fields=False)
    def validate_slippage_pre(cls, value):

        value = validation.get_converted_to_float(value, "Slippage")
        value = validation.get_positive(value, "Slippage", include_zero=False)
        value = validation.get_lower(value, 100, "Slippage", include_max=False)

        return value
