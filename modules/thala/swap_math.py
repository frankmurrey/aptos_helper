import math
from typing import Dict, List, Tuple, Union, Optional
from enum import Enum

from modules.thala.utils import convert_fp64_to_float
from modules.thala.pool_data_client import PoolDataClient


def get_d(t, n):
    e = len(t)
    r = sum(t)

    if r == 0:
        return 0

    i = r
    a = n * e
    o = 0

    while o < 100:
        n_i = i
        for c in range(e):
            n_i = (n_i * i) / (t[c] * e)

        new_i = ((a * r + e * n_i) * i) / ((a - 1) * i + (e + 1) * n_i)
        if abs(new_i - i) < 1e-6:
            return new_i

        i = new_i
        o += 1

    raise ValueError(f"not converged in getD, xp: {t}, a: {n}")


def get_y(t, n, e, r, i):

    a = get_d(t, e)
    o = len(t)
    c = e * o
    s = a
    l = 0
    u = 0

    while u < o:
        if u == i:
            u += 1
            continue
        e_val = n if u == r else t[u]
        l += e_val
        s = s * a / (e_val * o)
        u += 1

    s = s * a / (c * o)
    d = l + a / c
    p = a
    u = 0

    while u < 100:
        t_val = p
        p = (p * p + s) / (2 * p + d - a)
        if abs(p - t_val) < 1e-6:
            return p
        u += 1

    raise ValueError(f"not converged in getY, xp: {t}, x: {n}, a: {e}, i: {r}, j: {i}")


def calc_out_given_in_stable(
        input_amount: float,
        input_index: int,
        output_index: int,
        balances: list[float],
        amp: Union[float, int],
        swap_fee: float
) -> Union[float, None]:
    """
    Calculate the amount of output tokens given an exact amount of input tokens for a stable pool.
    :param input_amount:
    :param input_index:
    :param output_index:
    :param balances:
    :param amp:
    :param swap_fee:
    :return:
    """

    input_amount *= (1 - swap_fee)
    adjusted_input_balance = balances[input_index] + input_amount
    output_balance_after_swap = get_y(balances, adjusted_input_balance, amp, input_index, output_index)
    if output_balance_after_swap is None:
        return None

    return balances[output_index] - output_balance_after_swap


def calc_out_given_in_weighted(
        input_balance: float,
        input_weight: int,
        output_balance: float,
        output_weight: int,
        amount: float,
        swap_fee: float
) -> float:
    """
    Calculate the amount of output tokens given an exact amount of input tokens for a weighted pool.
    :param input_balance:
    :param input_weight:
    :param output_balance:
    :param output_weight:
    :param amount:
    :param swap_fee:
    :return:
    """
    return output_balance * (1 - math.pow(input_balance / (input_balance + amount * (1 - swap_fee)),
                                          input_weight / output_weight))

