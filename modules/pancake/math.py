def get_amount_in(
        amount_out: int,
        reserve_x: int,
        reserve_y: int
) -> int:
    """
    Calculates the amount of token X needed to buy token Y using the PancakeSwap formula.
    :param amount_out:
    :param reserve_x:
    :param reserve_y:
    :return:
    """
    amount_in_with_fee = amount_out * 9975

    numerator = amount_in_with_fee * int(reserve_y)
    denominator = int(reserve_x) * 10000 + amount_in_with_fee

    amount_in = numerator // denominator

    return amount_in


if __name__ == '__main__':
    print(get_amount_in(amount_out=100000000,
                        reserve_x=2287706544555,
                        reserve_y=2296291675453))
