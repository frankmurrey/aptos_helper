
def coins_sorted(
        coin_x_address: str,
        coin_y_address: str
) -> bool:
    """
    Sorts token X and Y by their addresses
    Args:
    token_a:
    token_b:

    Returns:

    """
    return coin_x_address.lower() < coin_y_address.lower()
