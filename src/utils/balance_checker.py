import os

from modules.base import AptosBase

from contracts.tokens import Tokens

from src.schemas.balance_checker import BalanceCheckerConfigSchema


import pandas as pd

from loguru import logger


def write_balance_data_to_xlsx(path,
                               data: list[dict],
                               coin_option):

    datapd = {
        "Wallet Address": [],
        "Balance": [],
        "Coin": []
    }

    for wallet in data:
        for addr, balance in wallet.items():
            datapd["Wallet Address"].append(addr)
            datapd["Balance"].append(balance)
            datapd["Coin"].append(coin_option)

    df = pd.DataFrame(datapd)
    try:
        df.to_excel(path, index=False)

        logger.warning(f"Balance data saved to {path}")
    except Exception as e:
        logger.error(f"Error while saving balance data to {path}: {e}")


class BalanceChecker(AptosBase):
    config: BalanceCheckerConfigSchema

    def __init__(self,
                 config,
                 base_url: str,
                 proxies: dict = None):
        super().__init__(base_url, proxies)
        self.coin_option = Tokens().get_by_name(config.coin_option)

    def get_balance_decimals(self, address):
        if not self.coin_option:
            return None

        coin_contract = self.coin_option.contract
        coin_decimals = self.get_token_decimals(token_obj=self.coin_option)

        wallet_coin_balance = self.get_wallet_token_balance(wallet_address=address,
                                                            token_contract=coin_contract)
        wallet_coin_balance_decimals = wallet_coin_balance / (10 ** coin_decimals)
        if wallet_coin_balance is None:
            logger.error(f"[{address}] - Error while getting balance of {self.coin_option.symbol.upper()}")

        else:
            logger.success(f"[{address}] - Balance: {wallet_coin_balance_decimals} {self.coin_option.symbol.upper()}")

        return wallet_coin_balance_decimals




