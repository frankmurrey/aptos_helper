from typing import List, Optional

from src import enums
from src.tasks_executor.base import TaskExecutorBase
from src.tasks_executor.multithread import task_executor_multi_thread
from src.tasks_executor.batch_multithread import task_executor_batch_multi_thread
from src.tasks_executor.singlethread import task_executor_single_thread
from src.tasks_executor.event_manager import TaskExecEventManager
from src.schemas.wallet_data import WalletData
from src.schemas.tasks import TaskBase


class TaskExecutor(TaskExecutorBase):
    """
    Wrapper for tasks executor
    """

    def __init__(self):
        super().__init__()

        self.actual_task_executor = task_executor_single_thread
        self.event_manager: Optional[TaskExecEventManager] = TaskExecEventManager()

        task_executor_single_thread.event_manager = self.event_manager
        task_executor_multi_thread.event_manager = self.event_manager

    def process_task(self, task: "TaskBase", wallet: "WalletData"):
        return self.actual_task_executor.process_task(task=task, wallet=wallet)

    def process_wallet(self, wallet: "WalletData", tasks: List["TaskBase"]):
        return self.actual_task_executor.process_wallet(wallet=wallet, tasks=tasks)

    def switch_task_executor(self, run_mode: enums.RunMode):
        """
        Switch task executor based on run mode
        Args:
            run_mode: mode to switch to
        Returns:

        """
        if run_mode == enums.RunMode.ASYNC:
            self.actual_task_executor = task_executor_multi_thread
        elif run_mode == enums.RunMode.SYNC:
            self.actual_task_executor = task_executor_single_thread
        else:
            raise ValueError(f"Unknown run mode: {run_mode}")

    def is_running(self) -> bool:
        return self.actual_task_executor.is_running()

    def process(
            self,
            wallets: List["WalletData"],
            tasks: List["TaskBase"],

            shuffle_wallets: bool = False,
            shuffle_tasks: bool = False,

            run_mode: Optional[enums.RunMode] = enums.RunMode.SYNC,
    ):
        self.switch_task_executor(run_mode)
        self.actual_task_executor.process(
            wallets=wallets,
            tasks=tasks,

            shuffle_wallets=shuffle_wallets,
            shuffle_tasks=shuffle_tasks,
        )

    def stop(self):
        self.actual_task_executor.stop()


task_executor = TaskExecutor()
