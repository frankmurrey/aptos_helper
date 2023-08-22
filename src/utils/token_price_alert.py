from typing import Union


class TokenPriceAlert:

    @staticmethod
    def is_target_price_valid(target_price: Union[int, float],
                              actual_gecko_price: Union[int, float, None],
                              max_price_difference_percent: Union[int, float],):
        try:
            if actual_gecko_price is None:
                return False

            if actual_gecko_price < target_price:
                return True

            if actual_gecko_price > target_price:
                price_difference = actual_gecko_price - target_price
                price_difference_percent = (price_difference / target_price) * 100
                if price_difference_percent <= max_price_difference_percent:
                    return True
                else:
                    return False

            return False

        except Exception as e:
            return False

