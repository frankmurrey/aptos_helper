def shorten_long_string(
        _: str,
        show_size: int = None,
        dots_size: int = None
) -> str:
    """
    This function takes a private key as input and shortens it by replacing a portion of the key with dots.

    Parameters:
    - private_key (str): The private key that needs to be shortened.

    Returns:
    - shortened_private_key (str): The shortened version of the private key.
    """
    show_size = show_size if show_size else int(len(_) / 10)
    dots_size = dots_size if dots_size else int(len(_) / 10)

    shortened_string = _[:show_size] + "." * dots_size + _[-show_size:]

    return shortened_string
