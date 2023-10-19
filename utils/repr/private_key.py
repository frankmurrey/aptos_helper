def blur_private_key(private_key: str) -> str:
    """
    This function takes a private key as input and blurs it by replacing a portion of the key with asterisks.

    Parameters:
    - private_key (str): The private key that needs to be blurred.

    Returns:
    - blurred_private_key (str): The blurred version of the private key.
    """
    length = len(private_key)
    start_index = length // 10
    end_index = length - start_index
    blurred_private_key = private_key[:start_index] + '*' * (end_index - start_index) + private_key[end_index + 4:]

    return blurred_private_key
