import time
import asyncio
import threading as th
from typing import Optional, List

from loguru import logger

from src.schemas.app_config import AppConfigSchema
from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.storage import Storage
from src.tasks_executor.base import TaskExecutorBase
from src.logger import configure_logger

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


class TaskExecutorBatchMultiThread(TaskExecutorBase):
    def __init__(
            self
    ):
        super().__init__()

        self.lock: Optional[th.Lock] = None

    def _start_processing(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],
    ):
        """
        Start processing async
        """

        Storage().update_app_config(config=AppConfigSchema(**self._app_config_dict))
        configure_logger()
        self.lock = th.Lock()

        wallet_threads = []
        for wallet_index, wallet in enumerate(wallets):
            clear_threads(wallet_threads, max_threads_num=config.DEFAULT_WALLETS_THREADS_NUM)
            is_last_wallet = wallet_index == len(wallets) - 1
            loop = asyncio.get_event_loop()

            thread = th.Thread(
                target=self.process_wallet,
                args=(
                    wallet,
                    tasks,

                    loop,
                )
            )

            if not is_last_wallet:
                time.sleep(config.DEFAULT_DELAY_SEC)

            thread.start()
            wallet_threads.append(thread)

        clear_threads(wallet_threads)
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
        self.wait_for_unlock()

        with self.lock:
            self.event_manager.set_wallet_started(wallet)

        self._process_wallet(wallet=wallet, tasks=tasks)
        self.event_manager.set_wallet_completed(wallet)

    def process_task(
            self,
            task: "TaskBase",
            wallet: "WalletData",
    ):
        self.event_manager.set_task_started(task, wallet)
        with self.lock:
            task_result = self._process_task(
                task=task,
                wallet=wallet,
            )
        self.event_manager.set_task_completed(task, wallet)

        return task_result

    def wait_for_unlock(self):
        while self.lock.locked():
            time.sleep(0.1)


task_executor_batch_multi_thread = TaskExecutorBatchMultiThread()
