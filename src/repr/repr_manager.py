import threading as th
from typing import List, Dict, Union, Optional
from typing import TYPE_CHECKING

from src.schemas.logs import LogRecord
from utils.repr import message as repr_message_utils

if TYPE_CHECKING:
    from src.schemas.wallet_data import WalletData
    from src.schemas.tasks.base.base import TaskBase
    from src.tasks_executor.event_manager import TaskExecEventManager


class ReprManager:
    by_thread_repr_items: Dict[int, List[Union[LogRecord, str]]] = {}

    @staticmethod
    def set_task_exec_callbacks(task_exec_event_manager: "TaskExecEventManager"):
        task_exec_event_manager.on_task_started(ReprManager.print_task_started_message)

    @staticmethod
    def print_logo_message():
        print(repr_message_utils.logo_message())

    @staticmethod
    def print_task_started_message(task: "TaskBase", wallet: "WalletData"):
        task_started_message = repr_message_utils.task_start_message(
            task=task,
            wallet=wallet,
        )
        print(task_started_message)

    @staticmethod
    def push_repr_item_to_thread_items(
            repr_item: Union[LogRecord, str],
            index: Optional[int] = None,
            thread: Optional[int] = None,
    ):
        """
        Push repr item to thread items
        Args:
            repr_item:
            index:
            thread:

        """

        if thread is None:
            thread = th.get_ident()

        if thread not in ReprManager.by_thread_repr_items:
            ReprManager.by_thread_repr_items[thread] = []

        if index is None:
            ReprManager.by_thread_repr_items[thread].append(repr_item)
        else:
            ReprManager.by_thread_repr_items[thread].insert(index, repr_item)

    @staticmethod
    def get_thread_repr_items(thread: Optional[int] = None):
        if thread is None:
            thread = th.get_ident()

        if thread in ReprManager.by_thread_repr_items:
            return ReprManager.by_thread_repr_items[thread]
        else:
            raise ValueError(f"Thread {thread} not found in ReprManager.by_thread_repr_items")

    @staticmethod
    def delete_thread_repr_items(thread: Optional[int] = None):
        if thread is None:
            thread = th.get_ident()

        if thread in ReprManager.by_thread_repr_items:
            del ReprManager.by_thread_repr_items[thread]
        else:
            raise ValueError(f"Thread {thread} not found in ReprManager.by_thread_repr_items")


repr_manager = ReprManager()
