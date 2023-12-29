from typing import Union


def calculate_market_skew(
        long_open_interest: int,
        short_open_interest: int
) -> int:
    return long_open_interest - short_open_interest


def calculate_leverage(
        amount_out_decimals: float,
        min_pay_usdt: Union[int, float]
) -> float:
    return 1 if amount_out_decimals > min_pay_usdt else min_pay_usdt / amount_out_decimals


def calculate_market_price(
        price_decimals: float,
        long_open_interest: int,
        short_open_interest: int,
        skew_factor: int
) -> float:
    market_skew = calculate_market_skew(long_open_interest, short_open_interest)
    return price_decimals * (1 + (market_skew / skew_factor))


def calculate_price_impact(
        market_skew: int,
        size_delta: int,
        skew_factor: int
) -> float:
    price_impact_before = market_skew / skew_factor
    price_impact_after = (market_skew + size_delta) / skew_factor
    price_impact = 0.5 * (price_impact_before + price_impact_after)
    return price_impact

