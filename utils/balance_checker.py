from typing import Union
from httpx import ConnectError

from loguru import logger
from aptos_sdk.account import AccountAddress
from aptos_sdk.client import ResourceNotFound

from aptos_rest_client.client import CustomRestClient
from contracts.tokens.main import Tokens
from contracts.base import TokenBase


class BalanceChecker:

    def __init__(
            self,
            coin_symbol: str,
            base_url: str,
            proxies: dict = None
    ):

        self.coin_option = Tokens().get_by_name(coin_symbol)

        self.client = CustomRestClient(base_url=base_url, proxies=proxies)

    def get_wallet_token_balance(
            self,
            wallet_address: AccountAddress,
            token_address: str,
    ) -> int:
        try:
            balance = self.client.account_resource(
                wallet_address,
                f"0x1::coin::CoinStore<{token_address}>",
            )
            return int(balance["data"]["coin"]["value"])

        except Exception as ex:
            logger.error(f"Error getting balance: {ex}")
            return 0

    def get_balance_decimals(self, address: AccountAddress) -> Union[int, None]:
        if not self.coin_option:
            return None

        coin_contract = self.coin_option.contract_address
        coin_decimals = self.get_token_decimals(token_obj=self.coin_option)

        wallet_coin_balance = self.get_wallet_token_balance(
            wallet_address=address,
            token_address=coin_contract
        )
        wallet_coin_balance_decimals = wallet_coin_balance / (10 ** coin_decimals)
        if wallet_coin_balance is None:
            logger.error(f"[{address}] - Error")

        else:
            logger.success(f"[{address}] - {round(wallet_coin_balance_decimals, 4)} {self.coin_option.symbol.upper()}")

        return wallet_coin_balance_decimals

    def get_token_decimals(self, token_obj: TokenBase) -> Union[int, None]:

        if token_obj.symbol == "aptos":
            return 8

        token_info = self.get_token_info(token_obj=token_obj)
        if not token_info:
            return None

        return token_info["decimals"]

    def get_token_info(self, token_obj: TokenBase) -> Union[dict, None]:
        if token_obj.symbol == "aptos":
            return None

        coin_address = self.get_address_from_hex(token_obj.address)

        try:
            token_info = self.client.account_resource(
                coin_address,
                f"0x1::coin::CoinInfo<{token_obj.contract_address}>",
            )
            return token_info["data"]

        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return None

    def get_address_from_hex(self, hex_address: str) -> AccountAddress:

        if hex_address.startswith("0x"):
            hex_address = hex_address[2:]
        return AccountAddress(bytes.fromhex(hex_address))
