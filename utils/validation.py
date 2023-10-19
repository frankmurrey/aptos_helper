import config
from src.exceptions import AppValidationError


def get_greater(value: float, then: float, field: str, include_min: bool = True):

    if include_min and value < then:
        raise AppValidationError(f"{field} should be >= {then}")

    elif not include_min and value <= then:
        raise AppValidationError(f"{field} should be > {then}")

    return value


def get_lower(value: float, then: float, field: str, include_max: bool = True):

    if include_max and value > then:
        raise AppValidationError(f"{field} should be <= {then}")

    elif not include_max and value >= then:
        raise AppValidationError(f"{field} should be < {then}")

    return value


def get_positive(value: float, field: str, include_zero: bool = True):
    return get_greater(value, 0, field, include_zero)


def get_converted_to_int(value: str, field: str):
    try:
        value = int(value)
        return value
    except ValueError:
        raise AppValidationError(f"{field} should be an integer")


def get_converted_to_float(value: str, field: str):
    try:
        value = float(value)
        return value
    except ValueError:
        raise AppValidationError(f"{field} should be a float")
