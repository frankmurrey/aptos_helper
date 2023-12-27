import random
from datetime import datetime, timedelta
from typing import Union
from typing import TYPE_CHECKING

from colorama import Fore

from utils.repr.color import Color
from utils.repr.misc import donation_messages
from utils.repr.private_key import blur_private_key
from utils.repr.module import module_config_table
import config

if TYPE_CHECKING:
    from src.schemas.wallet_data import WalletData
    from src.schemas.tasks.base import TaskBase


def logo() -> str:
    return '''
     ______   __  ___                          
    / ____/  /  |/  /_  _______________  __  __
   / /_     / /|_/ / / / / ___/ ___/ _ \/ / / /
  / __/    / /  / / /_/ / /  / /  /  __/ /_/ / 
 /_/      /_/  /_/\__,_/_/  /_/   \___/\__, /  
                                       /___/   '''


def logo_message() -> str:
    return f"{Fore.LIGHTMAGENTA_EX}{logo()}{Fore.RESET}\n"


def module_starting_delay_message(
    delay: Union[int, float] = config.DEFAULT_DELAY_SEC,
):
    return f"{Fore.LIGHTMAGENTA_EX}Starting in {delay} sec...{Fore.RESET}\n"


def task_exec_sleep_message(
        time_to_sleep: Union[int, float],
) -> str:
    continue_datetime = datetime.now() + timedelta(seconds=time_to_sleep)
    return (
        f"Time to sleep for {int(time_to_sleep)} seconds..."
        f" Continue at {continue_datetime.strftime('%H:%M:%S')}"
    )


def wallet_execution_message(
        wallet: "WalletData",
) -> str:
    msg = (
        f"\n"
        f"{Color.BORDER}[{Fore.RESET}"
        f"{wallet.index + 1}"
        f"{Color.BORDER}]{Fore.RESET} "
        f"{Color.CONFIG_KEY_COLOR}{wallet.name}{Fore.RESET}"
        f" - "
        f"{Color.CONFIG_VALUE_COLOR}{wallet.address}{Fore.RESET}"
    )
    msg += "\n"
    msg += (
        f"{Color.CONFIG_KEY_COLOR}PK{Fore.RESET}"
        f" - "
        f"{Color.CONFIG_VALUE_COLOR}{blur_private_key(wallet.private_key)}{Fore.RESET}"
    )

    return msg


def watermark_message() -> str:
    return f"{Fore.LIGHTMAGENTA_EX}Made by Frank Murrey - https://github.com/frankmurrey{Fore.RESET}"


def donation_message() -> str:
    message = random.choice(donation_messages)

    msg = (
        f"{Fore.LIGHTMAGENTA_EX}{message}{Fore.RESET}\n"
        f"{Fore.LIGHTMAGENTA_EX}EVM - 0xA7579FF5783e8bD48E5002a294A0b1054F820760 {Fore.RESET}\n"
        f"{Fore.LIGHTMAGENTA_EX}STARK - 0x062d04705B96734eba8622667E9Bc8fec78C77e4c5878B2c72eA84702C17db3b"
        f"{Fore.RESET}\n"
    )

    return msg


def task_start_message(
        task: "TaskBase",
        wallet: "WalletData",

        task_starting_delay: Union[int, float] = config.DEFAULT_DELAY_SEC,
        random_donation_message: bool = True,
) -> str:
    msg = (
        f"{wallet_execution_message(wallet)}\n"
        f"{module_config_table(task)}\n"
        f"{watermark_message()}\n"
    )

    if random_donation_message and random.randint(1, 8) == 1:
        msg += f"{donation_message()}\n"

    msg += f"{module_starting_delay_message(delay=task_starting_delay)}\n"

    return msg
