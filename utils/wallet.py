from typing import List

from src.schemas.wallet_data import WalletData


def set_wallets_indexes(wallets: List[WalletData]):
    """
    Set wallets indexes in wallets list
    Args:
        wallets: actual wallets
    Returns: wallets with indexes
    """
    for wallet_index, wallet in enumerate(wallets):
        wallet.index = wallet_index

    return wallets
