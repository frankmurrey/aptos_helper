from src.file_manager import FileManager
from src.paths import (TempFiles,
                       APP_CONFIG_FILE)
from src.schemas.app_config import AppConfigSchema


class Storage:
    __instance = None

    class __Singleton:
        DEFAULT_RPC_URL = '"https://rpc.ankr.com/http/aptos/v1"'

        def __init__(self):
            self.__wallets_data = FileManager().get_wallets_from_files()
            self.__shuffle_wallets = False
            self.__app_config = self.__load_app_config()

            __rpc_url_from_file = FileManager().read_data_from_json_file(TempFiles().RPC_URLS_JSON_FILE)
            self.__rpc_url = __rpc_url_from_file.get('APTOS') if __rpc_url_from_file else self.DEFAULT_RPC_URL

        def set_wallets_data(self, value):
            self.__wallets_data = value

        def set_shuffle_wallets(self, value):
            self.__shuffle_wallets = value

        def set_rpc_url(self, value):
            self.__rpc_url = value

        def get_wallets_data(self):
            return self.__wallets_data

        def get_shuffle_wallets(self):
            return self.__shuffle_wallets

        def get_rpc_url(self):
            return self.__rpc_url

        def get_app_config(self) -> AppConfigSchema:
            return self.__app_config

        def __load_app_config(self):
            try:
                config_file_data = FileManager().read_data_from_json_file(APP_CONFIG_FILE)
                return AppConfigSchema(**config_file_data)
            except Exception as e:
                raise e

    def __new__(cls):
        if not Storage.__instance:
            Storage.__instance = Storage.__Singleton()
        return Storage.__instance

