from math import pow

from decimal import Decimal, getcontext


def lp_value(
        x_coin: Decimal,
        x_scale: Decimal,
        y_coin: Decimal,
        y_scale: Decimal,
) -> Decimal:
    # Define the e8 constant
    e8 = Decimal(10 ** 8)

    x = x_coin * e8 // x_scale
    y = y_coin * e8 // y_scale
    a = x * y
    b = x * x + y * y

    return a * b


def coin_in(
        coin_out: Decimal,
        scale_out: Decimal,
        scale_in: Decimal,
        reserve_out: Decimal,
        reserve_in: Decimal,
) -> Decimal:
    # Define the e8 constant
    e8 = Decimal(10 ** 8)

    xy = lp_value(reserve_in, scale_in, reserve_out, scale_out)

    reserve_in_scaled = reserve_in * e8 // scale_in
    reserve_out_scaled = reserve_out * e8 // scale_out
    amount_out_scaled = coin_out * e8 // scale_out

    total_reserve = reserve_out_scaled - amount_out_scaled
    x = get_y(total_reserve, xy, reserve_in_scaled) - reserve_in_scaled
    return x * scale_in // e8


def coin_out(coin_in, scale_in, scale_out, reserve_in, reserve_out):
    getcontext().prec = 30

    e8 = Decimal(10) ** 8

    xy = lp_value(reserve_in, scale_in, reserve_out, scale_out)

    reserve_in = reserve_in * e8 // scale_in
    reserve_out = reserve_out * e8 // scale_out
    amount_in = coin_in * e8 // scale_in
    total_reserve = amount_in + reserve_in
    y = reserve_out - get_y(total_reserve, xy, reserve_out)  # Implement get_y() function if required

    return y * scale_out // e8


def d_stable(x0: Decimal, y: Decimal) -> Decimal:
    x3 = x0 * 3
    yy = y * y
    xyy3 = x3 * yy
    xxx = x0 * x0 * x0

    return xyy3 + xxx


def f(x0: Decimal, y: Decimal) -> Decimal:
    yyy = y * y * y
    a = x0 * yyy
    xxx = x0 * x0 * x0
    b = xxx * y
    return a + b


def get_y(x0: Decimal, xy: Decimal, y: Decimal) -> Decimal:
    # Set the precision for Decimal calculations
    getcontext().prec = 28  # You can adjust this value based on your requirements

    i = 0
    while i < 255:
        k = f(x0, y)

        dy = Decimal(0)
        if k < xy:
            dy = xy - k / d_stable(x0, y) + 1
            y += dy
        else:
            dy = (k - xy) / d_stable(x0, y)
            y -= dy

        if dy <= 1:
            return y

        i += 1

    return y


def d(value=None) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(0) if value is None else Decimal(value)


def get_coins_in_with_fees_stable(
        coin_out,
        reserve_out,
        reserve_in,
        coin_out_decimals,
        coin_in_decimals,
        pool_fee,
) -> Decimal:
    # Define the denominator constant
    DENOMINATOR = Decimal(10 ** 18)

    scale_out = d(pow(10, coin_out_decimals))
    scale_in = d(pow(10, coin_in_decimals))
    fee = d(pool_fee)

    r = coin_in(coin_out, scale_out, scale_in, reserve_out, reserve_in)
    return ((r + 1) * DENOMINATOR) / (DENOMINATOR - fee) + 1


def get_coins_out_with_fees_stable(
        coin_in: Decimal,
        reserve_in: Decimal,
        reserve_out: Decimal,
        scale_in: Decimal,
        scale_out: Decimal,
        fee: Decimal,
) -> Decimal:
    # Set the precision for Decimal calculations
    getcontext().prec = 28  # You can adjust this value based on your requirements

    # Define the denominator constant
    DENOMINATOR = Decimal(10 ** 18)

    coin_in_val_after_fees = Decimal(0)
    coin_in_val_scaled = coin_in * DENOMINATOR

    if coin_in_val_scaled % DENOMINATOR != 0:
        coin_in_val_after_fees = (coin_in_val_scaled // DENOMINATOR + 1) - (coin_in_val_scaled // DENOMINATOR + 1) * fee / 10000
    else:
        coin_in_val_after_fees = (coin_in_val_scaled // DENOMINATOR) - (coin_in_val_scaled // DENOMINATOR) * fee / 10000

    return coin_out(coin_in_val_after_fees, scale_in, scale_out, reserve_in, reserve_out)


def get_optimal_liquidity_amount(x_desired: Decimal,
                                 x_reserve: Decimal,
                                 y_reserve: Decimal) -> Decimal:
    return x_desired * y_reserve / x_reserve


if __name__ == '__main__':
    out_ = get_coins_out_with_fees_stable(
        coin_in=Decimal(337000000),
        reserve_in=Decimal(2332323707748),
        reserve_out=Decimal(1903323601400),
        scale_in=Decimal(1000000),
        scale_out=Decimal(1000000),
        fee=d(4)
    )
    print(out_)
    liq_ = get_optimal_liquidity_amount(
        x_desired=Decimal(180000000),
        x_reserve=Decimal(1899881601400),
        y_reserve=Decimal(2331737707748)
    )

