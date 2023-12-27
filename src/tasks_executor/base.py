import time
import random
import asyncio
import multiprocessing as mp
from abc import abstractmethod
from typing import Optional, List

from loguru import logger

from modules.module_executor import ModuleExecutor
from src.tasks_executor.event_manager import TaskExecEventManager
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.app_config import AppConfigSchema
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.storage import ActionStorage
from src.storage import Storage
from src.logger import configure_logger
from src import enums

from utils.repr import message as repr_message_utils
from utils import wallet as wallet_utils
from utils import task as task_utils

import config


class TaskExecutorBase:
    def __init__(self):
        self.processing_process: Optional[mp.Process] = None
        self.event_manager: Optional[TaskExecEventManager] = TaskExecEventManager()

        self._app_config_dict: Optional[dict] = None

    def _process_task(
            self,
            task: "TaskBase",
            wallet: "WalletData",
    ) -> ModuleExecutionResult:
        """
        Base method for task processing.
        Args:
            task: task to process
            wallet: wallet for task
        """
        task.task_status = enums.TaskStatus.PROCESSING

        logger.debug(f"Processing task: {task.task_id} with wallet: {wallet.name}")
        logger.bind(task=task).info(f"Task started")

        if random.randint(0, 100) > task.probability:
            task.task_status = enums.TaskStatus.SKIPPED

            return ModuleExecutionResult(
                execution_status=False,
                execution_info=f"Task was skipped by probability ({task.probability}%)",
            )

        module_executor = ModuleExecutor(task=task, wallet=wallet)

        loop = asyncio.get_event_loop()
        task_result_coroutine = module_executor.start()
        task_result: ModuleExecutionResult = loop.run_until_complete(task_result_coroutine)

        task_status = enums.TaskStatus.SUCCESS if task_result.execution_status else enums.TaskStatus.FAILED
        task.task_status = task_status
        task.result_hash = task_result.hash
        task.result_info = task_result.execution_info

        logger.bind(task=task).info(f"Task finished")

        return task_result

    def _process_wallet(
            self,
            wallet: "WalletData",
            tasks: List["TaskBase"],
    ):
        """
        Base method for wallet processing.
        Args:
            wallet: wallet to process
            tasks: list of tasks to process
        """
        for task_index, task in enumerate(tasks):
            task_result = self.process_task(
                task=task,
                wallet=wallet,
            )

            time_to_sleep = task_utils.get_time_to_sleep(task=task, task_result=task_result)
            is_last_task = task_index == len(tasks) - 1

            if not is_last_task:
                logger.info(repr_message_utils.task_exec_sleep_message(time_to_sleep))
                time.sleep(time_to_sleep)

    @abstractmethod
    def process_task(
            self,
            task: "TaskBase",
            wallet: "WalletData",
    ):
        """
        Process a task
        Args:
            task: task to process
            wallet: wallet for task
        """

    @abstractmethod
    def process_wallet(
            self,
            wallet: "WalletData",
            tasks: List["TaskBase"],
    ):
        """
        Process a wallet
        Args:
            wallet: wallet to process
            tasks: list of tasks to process
        """

    def _start_processing(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],
    ):
        """
        Start processing async
        """

        if tasks[0].test_mode is False:
            ActionStorage().reset_all_actions()
            ActionStorage().create_and_set_new_logs_dir()

        Storage().update_app_config(config=AppConfigSchema(**self._app_config_dict))
        configure_logger()

        for wallet_index, wallet in enumerate(wallets):
            self.process_wallet(
                wallet=wallet,
                tasks=tasks,
            )

            time_to_sleep = config.DEFAULT_DELAY_SEC
            is_last_wallet = wallet_index == len(wallets) - 1

            if not is_last_wallet:
                logger.info(repr_message_utils.task_exec_sleep_message(time_to_sleep))
                time.sleep(time_to_sleep)

        logger.success("All wallets processed")

    def is_running(self):
        """
        Is processing running
        """
        if isinstance(self.processing_process, mp.Process):
            is_alive = self.processing_process.is_alive()
            if not is_alive:
                self.processing_process = None
            return is_alive

        return self.processing_process is not None

    def process(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],

            shuffle_wallets: bool = False,
            shuffle_tasks: bool = False,
    ):
        """
        Process
        """
        logger.debug("Starting tasks executor")

        if shuffle_wallets:
            random.shuffle(wallets)

        if shuffle_tasks:
            random.shuffle(tasks)

        wallets = wallet_utils.set_wallets_indexes(wallets)
        tasks = task_utils.fill_with_virtual_tasks(tasks)

        self._app_config_dict = Storage().app_config.dict()

        self.processing_process = mp.Process(target=self._start_processing, args=(wallets, tasks))
        self.processing_process.start()
        self.event_manager.start()

    def stop(self):
        """
        Stop
        """
        self.event_manager.stop()

        if isinstance(self.processing_process, mp.Process):
            self.processing_process.terminate()

        if self.processing_process:
            self.processing_process.terminate()

        self.processing_process = None
