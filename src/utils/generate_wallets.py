from aptos_sdk.account import Account


def generate_keys(amount):
    return [Account.generate().private_key.hex() for _ in range(amount)]
