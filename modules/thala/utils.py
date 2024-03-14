import re
from decimal import Decimal
from typing import Union

FJ_PREFIX = "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af"

RE_WEIGHTED_POOL = re.compile(rf"{FJ_PREFIX}::weighted_pool::WeightedPool<(.*)>")
RE_STABLE_POOL = re.compile(rf"{FJ_PREFIX}::stable_pool::StablePool<(.*)>")
RE_BASE_POOL = re.compile(rf"{FJ_PREFIX}::base_pool::Null")
RE_WEIGHTED_POOL_TOKEN = re.compile(rf"{FJ_PREFIX}::weighted_pool::WeightedPoolToken<(.*)>")
RE_STABLE_POOL_TOKEN = re.compile(rf"{FJ_PREFIX}::stable_pool::StablePoolToken<(.*)>")


class PoolTypes:
    Weighted = "Weighted"
    Stable = "Stable"


def get_lp_coin_type(res_type: str) -> str:
    """
    Get the lp coin type of the liquidity pool
    :param res_type:
    :return:
    """
    n, e = parse_liquidity_pool_type(res_type)
    if n == PoolTypes.Weighted:
        return f"{FJ_PREFIX}::weighted_pool::WeightedPoolToken<{', '.join(e)}>"
    else:
        return f"{FJ_PREFIX}::stable_pool::StablePoolToken<{', '.join(e)}>"


def parse_liquidity_pool_type(res_type: str) -> (str, list):
    """
    Parse the liquidity pool type
    :param res_type:
    :return:
    """
    weighted_pattern = re.compile(RE_WEIGHTED_POOL)
    stable_pattern = re.compile(RE_STABLE_POOL)

    n = weighted_pattern.match(res_type)
    if n:
        return PoolTypes.Weighted, n.group(1).split(',')

    e = stable_pattern.match(res_type)
    if e:
        return PoolTypes.Stable, e.group(1).split(',')

    raise ValueError(f"Invalid poolType: {res_type}")


class C:
    def __init__(self):
        self.P = {'Weighted': "Weighted", 'Stable': "Stable", 'LBP': "LBP"}


c = C()


def convert_fp64_to_float(input_number: int) -> Union[float, None]:
    """
    Convert a 64-bit floating-point number to a Python float.
    :param input_number:
    :return:
    """
    ZERO = 0
    ONE = 1

    mask = int("0xffffffff000000000000000000000000", 16)

    if (input_number & mask) != ZERO:
        return None

    mask = int("0x10000000000000000", 16)
    bit_value = 1
    result = 0

    for i in range(32):
        if (input_number & mask) != ZERO:
            result += bit_value
        bit_value *= 2
        mask <<= ONE

    mask = int("0x8000000000000000", 16)
    bit_value = 0.5

    for i in range(32):
        if (input_number & mask) != ZERO:
            result += bit_value
        bit_value /= 2
        mask >>= ONE

    return result


i_a = Decimal(10)


def scale_down(t, n):

    return (Decimal(t) / i_a**n).to_eng_string()


def format_balances(t, n):
    return [scale_down(n['data'][f"asset_{r}"]['value'], asset['decimals']) for r, asset in enumerate(t)]



