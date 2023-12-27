import random

from enum import Enum

from colorama import Fore, Style

from src.schemas.tasks.base import TaskBase
from src.schemas.tasks.jediswap import JediSwapTask
from utils.repr.misc import donation_messages
from utils.repr.symbol import Symbol
from utils.repr.color import Color
import config


def get_border_top(width: int) -> str:
    repr_string = Color.BORDER

    repr_string += Symbol.left_top + Symbol.top * (width - 2) + Symbol.right_top

    repr_string += Fore.RESET

    return repr_string


def get_border_bottom(key_width: int, value_width: int) -> str:
    repr_string = Color.BORDER

    repr_string += Symbol.left_bottom
    repr_string += Symbol.bottom * (key_width + 3)
    repr_string += Symbol.bottom_middle
    repr_string += Symbol.bottom * (value_width + 3)
    repr_string += Symbol.right_bottom

    repr_string += Fore.RESET

    return repr_string


def get_border_middle(key_width: int, value_width: int) -> str:
    repr_string = Color.BORDER

    repr_string += Symbol.left_middle + Symbol.top * (key_width + 3) + Symbol.top_middle + Symbol.top * (value_width + 3) + Symbol.right_middle

    repr_string += Fore.RESET

    return repr_string


def get_module_name_header(module_name: str, width: int) -> str:

    if len(module_name) > config.MODULE_NAME_MAX_LENGTH:
        strip_size = int(config.MODULE_NAME_MAX_LENGTH / 2)
        module_name = f"{module_name[:strip_size - 1]}...{module_name[-strip_size+3:]}"

    module_name = f"{Color.MODULE_NAME}{module_name.capitalize()}"

    header_text = f"{module_name}"
    header_text += f"{Color.MODULE_HEADER_TEXT}'s module config"
    header_text += f"{Fore.RESET}"

    space_width = width - 4 + 3 * config.COLOR_LENGTH

    repr_string = Color.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    repr_string += f" {header_text:^{space_width}} "

    repr_string += Color.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    return repr_string


def get_max_width(max_key_width: int, max_value_width: int) -> int:
    return 2 + max_key_width + 5 + max_value_width + 2


def format_key(key: str, max_key_width: int) -> str:
    key = key.title().replace("_", " ")
    key = f"{Color.CONFIG_KEY_COLOR}{key}{Fore.RESET}"
    key_width = max_key_width + 2 * config.COLOR_LENGTH

    return f" {key:>{key_width + 1}} "


def format_value(value, max_value_width: int) -> str:
    value_width = max_value_width

    if issubclass(value.__class__, Enum):
        value = str(value.value).upper()

    if isinstance(value, bool):
        value_width = value_width + 2 * config.COLOR_LENGTH
        value = (f"{Fore.GREEN}+" if value else f"{Fore.RED}-") + Fore.RESET

    else:
        value_width += 2 * config.COLOR_LENGTH
        value = f"{Color.CONFIG_VALUE_COLOR}{value}{Fore.RESET}"

    return f" {value:<{value_width + 1}} "


def module_config_table(task: TaskBase):

    repr_strings = []

    task_dict = task.dict(exclude={
        "module_name",
        "module",
        "task_id",
        "task_status",
        "reverse_action_task",
        'result_info',
        'result_hash',
    })

    max_key_width = max(len(key) for key in task_dict.keys())
    max_value_width = max(len(str(value)) for value in task_dict.values())
    max_width = get_max_width(max_key_width, max_value_width)
    module_type = task_dict.pop("module_type")
    test_mode = task_dict.pop("test_mode")

    repr_string = Color.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    repr_string += format_key("module_type", max_key_width)

    repr_string += Color.BORDER
    repr_string += Symbol.center
    repr_string += Fore.RESET

    repr_string += format_value(module_type, max_value_width)

    repr_string += Color.BORDER
    repr_string += Symbol.right
    repr_string += Fore.RESET

    repr_strings.append(repr_string)

    for key, value in task_dict.items():

        repr_string = Color.BORDER
        repr_string += Symbol.left
        repr_string += Fore.RESET

        repr_string += format_key(key, max_key_width)

        repr_string += Color.BORDER
        repr_string += Symbol.center
        repr_string += Fore.RESET

        repr_string += format_value(value, max_value_width)

        repr_string += Color.BORDER
        repr_string += Symbol.right
        repr_string += Fore.RESET

        repr_strings.append(repr_string)

    repr_string = Color.BORDER
    repr_string += Symbol.left
    repr_string += Fore.RESET

    repr_string += format_key("test_mode", max_key_width)

    repr_string += Color.BORDER
    repr_string += Symbol.center
    repr_string += Fore.RESET

    repr_string += format_value(test_mode, max_value_width)

    repr_string += Color.BORDER
    repr_string += Symbol.right
    repr_string += Fore.RESET

    repr_strings.append(repr_string)

    repr_strings.insert(0, get_module_name_header(task.module_name, max_width))
    repr_strings.insert(0, get_border_top(max_width))
    repr_strings.insert(2, get_border_middle(key_width=max_key_width, value_width=max_value_width))
    repr_strings.append(get_border_bottom(key_width=max_key_width, value_width=max_value_width))

    repr_strings.insert(0, Style.BRIGHT)
    repr_strings.append(Style.BRIGHT)

    return "\n".join(repr_strings)

    print(*repr_strings, sep="\n")
    print(f"{Fore.LIGHTMAGENTA_EX}Made by Frank Murrey - https://github.com/frankmurrey{Fore.RESET}")

    if random.randint(1, 8) == 1:
        message = random.choice(donation_messages)
        print(f"{Fore.LIGHTMAGENTA_EX}{message}{Fore.RESET}\n")
        print(f"{Fore.LIGHTMAGENTA_EX}EVM - 0xA7579FF5783e8bD48E5002a294A0b1054F820760 {Fore.RESET}\n")
        print(f"{Fore.LIGHTMAGENTA_EX}STARK - 0x062d04705B96734eba8622667E9Bc8fec78C77e4c5878B2c72eA84702C17db3b"
              f"{Fore.RESET}\n")

    print(f"{Fore.LIGHTMAGENTA_EX}Starting in {config.DEFAULT_DELAY_SEC} sec...{Fore.RESET}\n")


if __name__ == '__main__':
    _task = JediSwapTask(
        coin_x='usdt',
        coin_y='eth',
        min_amount_out=0.1,
        max_amount_out=0.1,
        slippage=2,
        test_mode=True,
        max_fee=6000000,
        wait_for_receipt=True,
        txn_wait_timeout_sec=240,
        reverse_action=True,

    )
    print(module_config_table(_task))
