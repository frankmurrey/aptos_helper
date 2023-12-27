import time
import asyncio
import threading as th
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List

from loguru import logger

from src.schemas.app_config import AppConfigSchema
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.storage import Storage
from src.tasks_executor.base import TaskExecutorBase
from src.repr.repr_manager import ReprManager
from src.repr.event_manager import repr_event_manager
from src.logger import configure_threaded_task_executor_logger
from utils.repr import message as repr_message_utils

import config


def clear_threads(
    wallet_threads: List[th.Thread],
    max_threads_num: int = 0,
):
    """
    Clear executed wallet threads
    Args:
        wallet_threads: list of threads
        max_threads_num: max threads
    """
    while len(wallet_threads) >= max_threads_num:
        for thread_index, thread in enumerate(wallet_threads):
            if not thread.is_alive():
                wallet_threads.pop(thread_index)
        time.sleep(0.1)


class TaskExecutorMultiThread(TaskExecutorBase):
    def __init__(
            self
    ):
        super().__init__()

        self.lock: Optional[th.Lock] = None
        self.log_event_manager = repr_event_manager

    def _start_processing(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],
    ):
        """
        Start processing async
        """

        Storage().update_app_config(config=AppConfigSchema(**self._app_config_dict))
        configure_threaded_task_executor_logger(self.log_event_manager.queue)
        self.lock = th.Lock()

        with ThreadPoolExecutor(max_workers=config.DEFAULT_WALLETS_THREADS_NUM) as executor:
            futures = []
            for wallet_index, wallet in enumerate(wallets):
                loop = asyncio.get_event_loop()
                future = executor.submit(self.process_wallet, wallet, tasks, loop)
                futures.append(future)

                if wallet_index != len(wallets) - 1:
                    time.sleep(config.DEFAULT_DELAY_SEC)

        logger.success("All wallets processed")

    def process_wallet(
            self,
            wallet: "WalletData",
            tasks: List["TaskBase"],

            loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """
        Process a wallet
        Args:
            wallet: wallet to process
            tasks: list of tasks to process
            loop: asyncio loop
        """

        asyncio.set_event_loop(loop)

        self.event_manager.set_wallet_started(wallet)

        self._process_wallet(wallet=wallet, tasks=tasks)
        self.event_manager.set_wallet_completed(wallet)

    def process_task(
            self,
            task: "TaskBase",
            wallet: "WalletData",
    ):
        self.event_manager.set_task_started(task, wallet)

        ReprManager.push_repr_item_to_thread_items(
            repr_message_utils.task_start_message(
                task=task,
                wallet=wallet,
            ),
            thread=th.get_ident(),
        )
        task_result = self._process_task(
            task=task,
            wallet=wallet,
        )
        self.event_manager.set_task_completed(task, wallet)

        return task_result

    def wait_for_unlock(self):
        while self.lock.locked():
            time.sleep(0.1)


task_executor_multi_thread = TaskExecutorMultiThread()
