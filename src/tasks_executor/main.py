import random
import asyncio
import multiprocessing as mp
from datetime import datetime, timedelta
from typing import Optional, List

from loguru import logger

import config
from src import enums
from modules.module_executor import ModuleExecutor
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.storage import ActionStorage
from src.tasks_executor.event_manager import TasksExecEventManager
from utils.repr.misc import print_wallet_execution
from src.logger import configure_logger


class TasksExecutor:
    def __init__(self):
        self.processing_process: Optional[mp.Process] = None
        self.event_manager: Optional[TasksExecEventManager] = TasksExecEventManager()

    async def process_task(
            self,
            task: "TaskBase",
            wallet_index: int,
            wallet: "WalletData",

            is_last_task: bool = False,
    ):
        """
        Process a task
        Args:
            task: task to process
            wallet_index: index of wallet_
            wallet: wallet for task
            is_last_task: is current task the last
        """

        if wallet_index == 0 and task.test_mode is False:
            ActionStorage().reset_all_actions()
            ActionStorage().create_and_set_new_logs_dir()

        task.task_status = enums.TaskStatus.PROCESSING
        self.event_manager.set_task_started(task, wallet)

        logger.debug(f"Processing task: {task.task_id} with wallet: {wallet.name}")
        module_executor = ModuleExecutor(task=task, wallet=wallet)

        task_result = module_executor.start()

        task.task_status = enums.TaskStatus.SUCCESS if task_result else enums.TaskStatus.FAILED
        self.event_manager.set_task_completed(task, wallet)

        if not task_result or task.test_mode:
            time_to_sleep = config.DEFAULT_DELAY_SEC
        else:
            time_to_sleep = random.randint(
                task.min_delay_sec,
                task.max_delay_sec
            )

        if not is_last_task:
            continue_datetime = datetime.now() + timedelta(seconds=time_to_sleep)
            logger.info(f"Time to sleep for {time_to_sleep} seconds... "
                        f"Continue at {continue_datetime.strftime('%H:%M:%S')}")
            await asyncio.sleep(time_to_sleep)
        else:
            logger.success(f"All wallets and tasks completed!")

    async def process_wallet(
            self,
            wallet: "WalletData",
            wallet_index: int,
            tasks: List["TaskBase"],

            is_last_wallet: bool = False
    ):
        """
        Process a wallet
        Args:
            wallet: wallet to process
            wallet_index: index of wallet
            tasks: list of tasks to process
            is_last_wallet: is current wallet the last
        """
        self.event_manager.set_wallet_started(wallet)

        print_wallet_execution(wallet, wallet_index)

        for task_index, task in enumerate(tasks):
            await self.process_task(
                task=task,
                wallet_index=wallet_index,
                wallet=wallet,

                is_last_task=(task_index == len(tasks) - 1) and is_last_wallet,
            )

        self.event_manager.set_wallet_completed(wallet)

    async def _start_processing_async(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],
    ):
        """
        Start processing async
        """
        configure_logger()
        for wallet_index, wallet in enumerate(wallets):
            await self.process_wallet(
                wallet=wallet,
                wallet_index=wallet_index,
                tasks=tasks,

                is_last_wallet=wallet_index == len(wallets) - 1
            )

    def _start_processing(
        self,
        wallets: List["WalletData"],
        tasks: List["TaskBase"],
    ):
        """
        Start processing
        """
        asyncio.run(self._start_processing_async(wallets, tasks))

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


tasks_executor = TasksExecutor()
