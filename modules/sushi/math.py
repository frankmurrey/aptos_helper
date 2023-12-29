def get_amount_in(
        amount_out: int,
        reserve_in: int,
        reserve_out: int
) -> int:
    """
    Calculate the amount of token to be paid for a given amount of token
    Args:
    amount_out:
    reserve_in:
    reserve_out:

    Returns:

    """
    amount_in_with_fee = amount_out * 9975
    numerator = amount_in_with_fee * reserve_in
    denominator = reserve_out * 10000 + amount_in_with_fee
    return numerator // denominator


if __name__ == '__main__':
    res_x = 8293118693700
    res_y = 800502655571

    out = 10000000

    print(get_amount_in(
        reserve_out=res_x,
        reserve_in=res_y,
        amount_out=out
    ))