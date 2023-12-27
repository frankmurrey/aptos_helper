from typing import List

from src.tasks_executor.base import TaskExecutorBase
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.wallet_data import WalletData
from src.schemas.tasks import TaskBase


class TaskExecutorSingleThread(TaskExecutorBase):

    def process_task(
            self,
            task: "TaskBase",
            wallet: "WalletData",
    ) -> ModuleExecutionResult:

        self.event_manager.set_task_started(task, wallet)
        task_result = self._process_task(task=task, wallet=wallet)
        self.event_manager.set_task_completed(task, wallet)

        return task_result

    def process_wallet(
            self,
            wallet: "WalletData",
            tasks: List["TaskBase"],
    ):
        self.event_manager.set_wallet_started(wallet)
        self._process_wallet(wallet=wallet, tasks=tasks)
        self.event_manager.set_wallet_completed(wallet)


task_executor_single_thread = TaskExecutorSingleThread()
