from src.file_manager import FileManager
from src.paths import TempFiles


class WalletsStorage:
    __instance = None

    class __Singleton:
        DEFAULT_RPC_URL = '"https://rpc.ankr.com/http/aptos/v1"'

        def __init__(self):
            self.__wallets_data = FileManager().get_wallets_from_files()
            self.__shuffle_wallets = False

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

    def __new__(cls):
        if not WalletsStorage.__instance:
            WalletsStorage.__instance = WalletsStorage.__Singleton()
        return WalletsStorage.__instance


if __name__ == '__main__':
    WalletsStorage()