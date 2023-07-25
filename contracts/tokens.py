from contracts.base import Token
from src.file_manager import FileManager
from src.paths import TempFiles

from loguru import logger


class Tokens:
    def __init__(self):
        self.all_tokens_data_from_file = FileManager().read_data_from_json_file(TempFiles().TOKENS_JSON_FILE)
        self.all_tokens = self._get_all_token_objs()

    def _get_all_token_objs(self):
        if not self.all_tokens_data_from_file:
            raise ValueError("No tokens found, please add valid tokens in contracts/tokens.json file")

        try:
            all_token_objs = []
            for token_data in self.all_tokens_data_from_file:
                token_obj = Token(**token_data)
                all_token_objs.append(token_obj)

            return all_token_objs
        except Exception as e:
            logger.error(f"Error while creating token objects: {e}")
            exit(1)

    def get_by_name(self, name_query):
        for token in self.all_tokens:
            if token.symbol.lower() == name_query.lower():
                return token
        logger.error(f"Token {name_query} not found")
        return None

    def get_by_contract(self, contract_query):
        for token in self.all_tokens:
            if token.contract.lower() == contract_query.lower():
                return token
        logger.error(f"Token {contract_query} not found")
        return None

    def get_pancake_available_coins(self) -> list:
        return [token for token in self.all_tokens if token.is_pancake_available]

    def get_aptos_bridge_available_coins(self) -> list:
        return [token for token in self.all_tokens if token.aptos_bridge_handle is not None]

    def get_abel_finance_available_coins(self) -> list:
        return [token for token in self.all_tokens if token.is_abel_available]

    def get_thala_available_coins(self) -> list:
        return [token for token in self.all_tokens if token.is_thala_available]

    def get_liquid_swap_available_coins(self) -> list:
        return [token for token in self.all_tokens if token.is_liquid_swap_available]
