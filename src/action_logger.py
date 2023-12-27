from src.storage import Storage
from src.storage import ActionStorage
from src.schemas.logs import WalletActionSchema
from utils.xlsx import write_wallet_action_to_xlsx
from utils.file_manager import FileManager

from loguru import logger


class ActionLogger:

    def __init__(self):
        self.action_storage = ActionStorage()
        self.app_config = Storage().app_config

    def build_single_log(self, action_data) -> list:
        return [
            action_data.wallet_address,
            action_data.proxy,
            action_data.date_time,
            action_data.is_success,
            action_data.transaction_hash,
            action_data.action_type
        ]

    def save_single_log_to_csv(self, action_data):
        log = self.build_single_log(action_data)
        file_name = f"{action_data.wallet_address}_{action_data.date_time}.csv"
        path = self.action_storage.get_current_logs_dir()
        if not path:
            logger.error("No logs dir found")
            return

        FileManager().write_data_to_csv(
            path=path,
            file_name=file_name,
            data=log
        )

    def log_error(self, action_data: WalletActionSchema):
        if self.app_config.preserve_logs is False:
            return

        self.action_storage.update_current_action(action_data)
        write_wallet_action_to_xlsx()

        logger.info(f"Logged and saved wallet action in {self.action_storage.get_current_logs_dir()}")

    def add_action_to_log_storage(self, action_data: WalletActionSchema):
        if self.app_config.preserve_logs is False:
            return

        self.action_storage.add_action(action_data)

    @staticmethod
    def log_action_from_storage():
        write_wallet_action_to_xlsx()
        logger.info(f"Logged and saved wallet action in {ActionStorage().get_current_logs_dir()}")
