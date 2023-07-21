class Coin:
    def __init__(self, value):
        self.value = value

    def extract(self, amount):
        assert amount <= self.value, "Extraction amount exceeds available asset value"
        self.value -= amount
        return amount


class FixedPoint64:
    def __init__(self, v):
        self.v = v


class Pool:
    def __init__(self, asset_0, asset_1, asset_2, asset_3):
        self.asset_0 = asset_0
        self.asset_1 = asset_1
        self.asset_2 = asset_2
        self.asset_3 = asset_3


class Math:
    @staticmethod
    def value(coin):
        return coin.value

    @staticmethod
    def decode_round_down(fp_number):
        return fp_number.v

    @staticmethod
    def mul(fp_num1, num2):
        return FixedPoint64((fp_num1.v * num2) >> 64)

    @staticmethod
    def fraction(numerator, denominator):
        assert denominator != 0, "Division by zero error"

        r = numerator << 64
        v = r // denominator
        return FixedPoint64(v)


def get_pair_amount_in(lp_ratio,
                       lp_balance_x,
                       lp_balance_y, ):
    pool = Pool(Coin(lp_balance_x), Coin(lp_balance_y), Coin(0), Coin(0))

    amount_0 = Math.decode_round_down(Math.mul(lp_ratio, Math.value(pool.asset_0)))
    amount_1 = Math.decode_round_down(Math.mul(lp_ratio, Math.value(pool.asset_1)))
    out_0 = pool.asset_0.extract(amount_0)
    out_1 = pool.asset_1.extract(amount_1)
    return out_0, out_1

