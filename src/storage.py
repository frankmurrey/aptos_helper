import os
from typing import List

from loguru import logger

from src import paths
from src.schemas.app_config import AppConfigSchema
from src.schemas.logs import WalletActionSchema
from utils.file_manager import FileManager


class Storage:
    __instance = None

    class __Singleton:

        def __init__(self):
            self.__app_config: AppConfigSchema = self.__load_app_config()

        @property
        def app_config(self) -> AppConfigSchema:
            return self.__app_config

        def __load_app_config(self) -> AppConfigSchema:
            try:
                if os.path.exists(paths.APP_CONFIG_FILE):
                    config_file_data = FileManager.read_data_from_json_file(paths.APP_CONFIG_FILE)
                    return AppConfigSchema(**config_file_data)
            except Exception as e:
                logger.error(f"Error while loading app config: {e}")
                logger.exception(e)

        def update_app_config(self, config: AppConfigSchema):
            self.__app_config = config

        def update_app_config_values(self, **kwargs):
            if not self.__app_config:
                return
            config_dict = self.__app_config.dict()
            new_config_dict = {**config_dict, **kwargs}
            self.__app_config = AppConfigSchema(**new_config_dict)

    def __new__(cls):
        if not Storage.__instance:
            Storage.__instance = Storage.__Singleton()
        return Storage.__instance


class ActionStorage:
    __instance = None

    def __new__(cls):
        if not ActionStorage.__instance:
            ActionStorage.__instance = ActionStorage.__Singleton()
        return ActionStorage.__instance

    class __Singleton:

        def __init__(self):
            self.all_actions = []
            self.current_action: WalletActionSchema = WalletActionSchema()
            self.current_logs_dir = None
            self.current_active_wallet = None

        def set_current_active_wallet(self, wallet_data):
            self.current_active_wallet = wallet_data

        def get_current_active_wallet(self):
            return self.current_active_wallet

        def add_action(self, action_data: WalletActionSchema):
            if Storage().app_config.preserve_logs is False:
                return

            self.all_actions.append(action_data)

        def get_all_actions(self):
            return self.all_actions

        def get_current_action(self) -> WalletActionSchema:
            return self.current_action

        def update_current_action(self, action_data: WalletActionSchema):
            if Storage().app_config.preserve_logs is False:
                return

            self.current_action = action_data

        def set_current_logs_dir(self, new_logs_dir):
            if not os.path.exists(new_logs_dir):
                logger.error(f"Logs dir \"{new_logs_dir}\" does not exist")
                return

            self.current_logs_dir = new_logs_dir
            logger.info(f"Current logs dir set to {new_logs_dir}")

        def get_current_logs_dir(self):
            return self.current_logs_dir

        def reset_all_actions(self):
            self.all_actions = []

        def reset_current_logs_dir(self):
            self.current_logs_dir = None

        def create_and_set_new_logs_dir(self):
            if Storage().app_config.preserve_logs is False:
                return

            self.set_current_logs_dir(FileManager.create_new_logs_dir())

