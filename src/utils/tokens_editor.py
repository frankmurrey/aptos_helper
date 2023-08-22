from src.file_manager import FileManager
from src.paths import TempFiles

from contracts.tokens import Tokens
from contracts.base import Token


class TokensEditor:
    def __init__(self):
        self.tokens_json_path = TempFiles().TOKENS_JSON_FILE
        self.tokens_json_data = FileManager().read_data_from_json_file(self.tokens_json_path)

    def add_new_token(self, token: Token):
        if not self.is_token_symbol_exist_in_json(token.symbol):
            token_data = {
                "symbol": token.symbol,
                "contract": token.contract,
                "is_pancake_available": token.is_pancake_available,
                "is_abel_available": token.is_abel_available,
                "is_thala_available": token.is_thala_available,
                "is_liquid_swap_available": token.is_liquid_swap_available,
                'gecko_id': token.gecko_id

            }
            self.tokens_json_data.append(token_data)
            FileManager().write_data_to_json_file(self.tokens_json_path, self.tokens_json_data)
            Tokens().update_tokens_data()
            return True

        return False

    def is_token_symbol_exist_in_json(self, token_symbol: str):
        return token_symbol.lower() in [token['symbol'].lower() for token in self.tokens_json_data]

    def remove_token(self, token_symbol: str):
        if self.is_token_symbol_exist_in_json(token_symbol):
            self.tokens_json_data = [token for token in self.tokens_json_data if
                                     token['symbol'].lower() != token_symbol.lower()]
            FileManager().write_data_to_json_file(self.tokens_json_path, self.tokens_json_data)
            Tokens().update_tokens_data()
            return True

        return False
