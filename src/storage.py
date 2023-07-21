from src.file_manager import FileManager


class WalletsStorage:
    __instance = None

    class __Singleton:
        def __init__(self):
            self.__wallets_data = FileManager().get_wallets()
            self.__shuffle_wallets = False
            self.__rpc_url = "https://rpc.ankr.com/http/aptos/v1"

        def set_wallets_data(self, value):
            self.__wallets_data = value

        def set_shuffle_wallets(self, value):
            self.__shuffle_wallets = value

        def get_wallets_data(self):
            return self.__wallets_data

        def get_shuffle_wallets(self):
            return self.__shuffle_wallets

    def __new__(cls):
        if not WalletsStorage.__instance:
            WalletsStorage.__instance = WalletsStorage.__Singleton()
        return WalletsStorage.__instance
