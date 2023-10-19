import re
from typing import Union

from aptos_sdk.account import Account, AccountAddress


def detect_separator(
        filename: str,
        possible_delimiters: list[str]
) -> Union[str, None]:
    with open(filename, 'r', newline='') as file:
        first_line = file.readline()
        for delimiter in possible_delimiters:
            if re.search(f"[{delimiter}]", first_line):
                return delimiter

    return None


