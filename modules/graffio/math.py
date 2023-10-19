from typing import Union

import numpy as np


def get_random_coord(max_pixels: int) -> tuple:
    x = np.random.randint(0, max_pixels)
    y = np.random.randint(0, max_pixels)

    random_prefix = np.random.randint(0, 8)

    x = [int(x) + random_prefix]
    y = [int(y) + random_prefix]

    return list(x), list(y)


if __name__ == '__main__':
    x, y = get_random_letter(100)
    print(x, y)

