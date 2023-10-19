def get_short_addr(addr: str) -> str:
    try:
        return addr[:8] + "..." + addr[-8:]

    except IndexError:
        return addr
