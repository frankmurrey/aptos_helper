import time
import queue
import warnings
import threading as th
import multiprocessing as mp
from typing import Optional
from typing import Callable
from typing import Tuple

from loguru import logger

from src.schemas.tasks import TaskBase
from src.schemas.wallet_data import WalletData
from src.internal_queue import InternalQueue


def state_setter(obj: "TasksExecEventManager", state: dict):
    obj.running = state["running"]

    obj.wallets_started_queue = state["wallets_started_queue"]
    obj.tasks_started_queue = state["tasks_started_queue"]

    obj.wallets_completed_queue = state["wallets_completed_queue"]
    obj.tasks_completed_queue = state["tasks_completed_queue"]


class TasksExecEventManager:
    def __init__(self):
        self.running = mp.Event()
        self.listening_thread: Optional[th.Thread] = None

        self.wallets_started_queue = InternalQueue[Tuple[WalletData]]()
        self.tasks_started_queue = InternalQueue[Tuple[TaskBase, WalletData]]()

        self.wallets_completed_queue = InternalQueue[Tuple[WalletData]]()
        self.tasks_completed_queue = InternalQueue[Tuple[TaskBase, WalletData]]()

        self._on_wallet_started: Optional[Callable[[WalletData], None]] = self.pseudo_callback
        self._on_task_started: Optional[Callable[[TaskBase, WalletData], None]] = self.pseudo_callback

        self._on_wallet_completed: Optional[Callable[[WalletData], None]] = self.pseudo_callback
        self._on_task_completed: Optional[Callable[[TaskBase, WalletData], None]] = self.pseudo_callback

    def pseudo_callback(self, *args, **kwargs):
        """
        Placeholder method for a completed callback function.
        """
        logger.warning("Pseudo completed callback called.")

    # CALLBACKS SETTERS
    def on_wallet_started(self, callback: Callable[[WalletData], None]):
        """
        Set a callback function to be called when a wallet is started.

        Args:
            callback (Callable[[WalletData], None]): The callback function to be called when a wallet is started.
        """
        self._on_wallet_started = callback

    def on_task_started(self, callback: Callable[[TaskBase, WalletData], None]):
        """
        Set a callback function to be called when a task is started.

        Args:
            callback (Callable[[TaskBase, WalletData], None]): The callback function to be called when a task is started.
        """
        self._on_task_started = callback

    def on_wallet_completed(self, callback: Callable[[WalletData], None]):
        """
        Set a callback function to be called when a wallet is completed.

        Args:
            callback (Callable[[WalletData], None]): The callback function to be called when a wallet is completed.
        """
        self._on_wallet_completed = callback

    def on_task_completed(self, callback: Callable[[TaskBase, WalletData], None]):
        """
        Set a callback function to be called when a task is completed.

        Args:
            callback (Callable[[TaskBase, WalletData], None]): The callback function to be called when a task is completed.
        """
        self._on_task_completed = callback

    # EVENT CREATORS
    def set_wallet_started(self, wallet: WalletData):
        """
        Add a wallet to the 'wallets_started_queue'.

        Args:
            wallet (WalletData): The wallet to be added to the queue.
        """
        self.wallets_started_queue.put_nowait((wallet,))

    def set_task_started(self, task: TaskBase, wallet: WalletData):
        """
        Add a task and associated wallet to the 'tasks_started_queue'.

        Args:
            task (TaskBase): The task that was started.
            wallet (WalletData): The wallet associated with the task.
        """
        self.tasks_started_queue.put_nowait((task, wallet))

    def set_wallet_completed(self, wallet: WalletData):
        """
        Add a wallet to the 'wallets_completed_queue'.

        Args:
            wallet (WalletData): The wallet to be added to the queue.
        """
        self.wallets_completed_queue.put_nowait((wallet,))

    def set_task_completed(self, task: TaskBase, wallet: WalletData):
        """
        Add a task and associated wallet to the 'tasks_completed_queue'.

        Args:
            task (TaskBase): The task that was completed.
            wallet (WalletData): The wallet associated with the task.
        """
        self.tasks_completed_queue.put_nowait((task, wallet))

    def _process_queue_item(self, queue_name: str, callback: Callable):
        """
        Process an item from a queue and call the given callback function.

        Args:
            queue_name (str): The name of the queue to process.
            callback (Callable): The callback function to call with the queue item.
        """
        try:
            _queue: InternalQueue = getattr(self, queue_name)
            queue_item: Tuple = _queue.get_nowait()
            callback(*queue_item) if self.running else None

        except queue.Empty:
            time.sleep(0.1)

    def listen_for_event_items(self):
        """
        Listen for started and completed tasks and wallets
        """
        logger.debug("Listening thread started")

        while self.running.is_set():
            self._process_queue_item("wallets_started_queue", self._on_wallet_started)
            self._process_queue_item("tasks_started_queue", self._on_task_started)
            self._process_queue_item("wallets_completed_queue", self._on_wallet_completed)
            self._process_queue_item("tasks_completed_queue", self._on_task_completed)

        logger.debug("Listening thread stopped")

    def start(self):
        """
        Start the listening thread
        """
        self.running.set()
        self.listening_thread = th.Thread(target=self.listen_for_event_items)
        self.listening_thread.start()

    def stop(self):
        """
        Stop the listening thread
        """
        self.running.clear()

    def __reduce__(self):
        return (
            object.__new__,
            (type(self),),
            {
                "running": self.running,

                # queues
                "wallets_started_queue": self.wallets_started_queue,
                "tasks_started_queue": self.tasks_started_queue,
                "wallets_completed_queue": self.wallets_completed_queue,
                "tasks_completed_queue": self.tasks_completed_queue,
            },
            None,
            None,
            state_setter,
        )