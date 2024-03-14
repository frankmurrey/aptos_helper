import time
from typing import Union
from colorama import Fore


def gas_price_wait_loop(
    target_price_wei: Union[int, float],
    current_gas_price: Union[int, float],
    time_out_sec: Union[int, float] = None,
    end: str = ''
):

    t_len = len(str(time_out_sec))

    target_gas_price_str = f"{Fore.LIGHTCYAN_EX}{target_price_wei} GWEI{Fore.RESET}"
    current_gas_price_str = f"{Fore.LIGHTCYAN_EX}{current_gas_price} GWEI{Fore.RESET}"

    info_message = Fore.LIGHTMAGENTA_EX + "Waiting for gas price < "
    info_message += target_gas_price_str

    info_message += Fore.LIGHTMAGENTA_EX + ". Last checked gas price: "
    info_message += current_gas_price_str

    for i in range(time_out_sec):
        iter_message = f"\r{Fore.LIGHTCYAN_EX}[{i:{t_len}}s/{time_out_sec}]"
        iter_message += Fore.RESET

        iter_message += Fore.RED + " - "
        iter_message += Fore.RESET

        iter_message += info_message

        print(iter_message, end='')
        time.sleep(1)

    iter_message = f"\r{Fore.LIGHTCYAN_EX}[{time_out_sec:{t_len}}s/{time_out_sec}]"
    iter_message += Fore.RESET

    iter_message += Fore.RED + " - "
    iter_message += Fore.RESET

    iter_message += info_message

    print(f"\r[{time_out_sec:{t_len}}s/{time_out_sec}] | {iter_message}", end=end)
