from typing import List, Dict, Any

from pydantic.error_wrappers import ValidationError
from tkinter import messagebox

from src.schemas.wallet_data import WalletData


class WalletManager:

    @staticmethod
    def get_wallets(wallets_data: List[Dict[str, Any]]):
        try:
            wallets = [
                WalletData(**wallet_item)
                for wallet_item in wallets_data
            ]
            return wallets

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None

