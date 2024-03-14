import time
from datetime import datetime

from aptos_sdk.account import Account
from loguru import logger


from src.schemas.tasks.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.schemas.logs import WalletActionSchema
from src.schemas.action_models import ModuleExecutionResult
from src.storage import Storage
from src.storage import ActionStorage
from src.action_logger import ActionLogger
from src.proxy_manager import ProxyManager

import config as cfg


class ModuleExecutor:
    """
    Module executor for modules
    """

    def __init__(
            self,
            task: TaskBase,
            wallet: WalletData
    ):
        self.task = task
        self.module_name = task.module_name
        self.module_type = task.module_type
        self.storage = Storage()
        self.action_storage = ActionStorage()

        self.app_config = self.storage.app_config

        self.wallet_data = wallet

    async def start(self) -> ModuleExecutionResult:
        time.sleep(cfg.DEFAULT_DELAY_SEC)

        if not self.app_config.rpc_url:
            logger.error("Please, set RPC URL in tools window or app_config.json file")
            return ModuleExecutionResult(
                execution_status=False,
                execution_info="Set RPC URL in tools window or app_config.json file",
            )

        execute_status = self.execute_module(
            wallet_data=self.wallet_data, base_url=self.app_config.rpc_url
        )

        return execute_status

    def execute_module(
            self,
            wallet_data: WalletData,
            base_url: str
    ) -> ModuleExecutionResult:
        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data)
        proxies = proxy_manager.get_proxy()

        action_log_data = WalletActionSchema(
            date_time=datetime.now().strftime("%d-%m-%Y_%H-%M-%S"),
            wallet_address=wallet_data.address,
        )

        self.action_storage.update_current_action(action_data=action_log_data)

        current_ip = proxy_manager.get_ip()
        if current_ip is None and proxy_data:
            err_msg = f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params"
            action_log_data.set_error(err_msg)

            action_log_data.module_name = self.module_name.value
            action_log_data.module_type = self.module_type.value

            action_log_data.is_success = False
            action_log_data.status = err_msg

            action_logger = ActionLogger()
            action_logger.add_action_to_log_storage(action_data=action_log_data)
            action_logger.log_action_from_storage()

            return ModuleExecutionResult(
                execution_status=False,
                execution_info=err_msg,
            )

        logger.info(f"Current ip: {current_ip}\n")

        account = Account.load_key(wallet_data.private_key)
        retries = self.task.retries if self.task.test_mode is False else 1

        execution_status: ModuleExecutionResult
        module = self.task.module(
            account=account,
            task=self.task,
            base_url=base_url,
            proxies=proxies,
            wallet_data=wallet_data
        )
        execution_status = module.try_send_txn(retries=retries)

        if self.task.test_mode is False:
            action_log_data.module_name = self.module_name.value
            action_log_data.module_type = self.module_type.value

            action_log_data.is_success = execution_status.execution_status
            action_log_data.status = execution_status.execution_info
            action_log_data.transaction_hash = execution_status.hash

            action_logger = ActionLogger()
            action_logger.add_action_to_log_storage(action_data=action_log_data)
            action_logger.log_action_from_storage()

        return execution_status
