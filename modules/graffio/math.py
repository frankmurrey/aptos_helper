from typing import Union

import numpy as np
import matplotlib.pyplot as plt


def get_random_letter(n_max: int) -> Union[None, tuple]:
    max_pixels = n_max
    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    np.random.shuffle(letters)

    for letter in letters:
        fig, ax = plt.subplots(figsize=(0.5, 0.5))
        ax.axis('off')
        ax.text(0.5, 0.5, letter, ha='center', va='center', fontsize=20)

        fig.canvas.draw()

        data = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(
            fig.canvas.get_width_height()[::-1] + (4,))
        plt.close(fig)

        gray = np.dot(data[..., :3], [0.299, 0.587, 0.114])
        binary = gray < 128

        y, x = np.where(binary)

        random_prefix = np.random.randint(0, 900)

        y = [int(i) + random_prefix for i in y]
        x = [int(i) + random_prefix for i in x]

        if len(x) <= max_pixels:
            return list(x), list(y)

    return None


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

