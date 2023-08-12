import os
import pandas as pd

from datetime import datetime

from src.schemas.wallet_log import WalletActionSchema
from src.file_manager import FileManager
from src.paths import LOGS_DIR
from src.storage import Storage

from loguru import logger


def log_all_actions_to_xlsx():
    action_storage = ActionStorage()
    all_actions = action_storage.get_all_actions()

    if not all_actions:
        return

    data = {
        "Wallet Address": [],
        "Proxy": [],
        "Date Time": [],
        "Action Type": [],
        "Is Success": [],
        "Transaction Hash": []
    }

    for action in all_actions:
        data["Wallet Address"].append(action.wallet_address)
        data["Proxy"].append(action.proxy)
        data["Date Time"].append(action.date_time)
        data["Action Type"].append(action.action_type)
        data["Is Success"].append(action.is_success)
        data["Transaction Hash"].append(action.transaction_hash)
    try:
        df = pd.DataFrame(data)
        df.to_excel(f"{action_storage.get_current_logs_dir()}\\!all_logs.xlsx", index=False)
    except Exception as e:
        logger.error(f"Error while logging all actions to xlsx: {e}")


def create_new_logs_dir():
    app_config = Storage().get_app_config()
    if app_config.preserve_logs is False:
        return

    date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    new_logs_dir = f"{LOGS_DIR}\\log_{date_time}"
    os.mkdir(new_logs_dir)

    if not os.path.exists(new_logs_dir):
        return
    return new_logs_dir


class ActionStorage:
    __instance = None

    def __new__(cls):
        if not ActionStorage.__instance:
            ActionStorage.__instance = ActionStorage.__Singleton()
        return ActionStorage.__instance

    class __Singleton:

        def __init__(self):
            self.all_actions = []
            self.current_logs_dir = None

        def add_action(self, action_data: WalletActionSchema):
            if not self.current_logs_dir:
                self.current_logs_dir = create_new_logs_dir()

            self.all_actions.append(action_data)

        def get_all_actions(self):
            return self.all_actions

        def set_current_logs_dir(self, new_logs_dir):
            if not os.path.exists(new_logs_dir):
                return

            self.current_logs_dir = new_logs_dir

        def get_current_logs_dir(self):
            return self.current_logs_dir

        def reset_storage(self):
            self.all_actions = []
            self.current_logs_dir = None


class ActionLogger:
    action_data: WalletActionSchema

    def __init__(self,
                 action_data):
        self.action_data = action_data
        self.action_storage = ActionStorage()

    def build_single_log(self) -> list:
        return [self.action_data.wallet_address,
                self.action_data.proxy,
                self.action_data.date_time,
                self.action_data.is_success,
                self.action_data.transaction_hash,
                self.action_data.action_type]

    def create_and_set_new_logs_dir(self):
        self.action_storage.set_current_logs_dir(create_new_logs_dir())

    def save_single_log_to_csv(self):
        log = self.build_single_log()
        file_name = f"{self.action_data.wallet_address}_{self.action_data.date_time}.csv"
        path = self.action_storage.get_current_logs_dir()
        if not path:
            logger.error("No logs dir found")
            return

        FileManager().write_data_to_csv(path=path,
                                        file_name=file_name,
                                        data=log)

    def log_action(self):
        app_config = Storage().get_app_config()
        if app_config.preserve_logs is False:
            return

        self.action_storage.add_action(self.action_data)
        self.save_single_log_to_csv()
        logger.debug(f"Logged and saved wallet action in {self.action_storage.get_current_logs_dir()}")
