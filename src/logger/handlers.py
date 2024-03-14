import threading as th
from typing import Optional, List, Union
from typing import TYPE_CHECKING

from src.schemas.logs import LogRecord
from src.repr.repr_manager import ReprManager
from src.internal_queue import InternalQueue
from src import enums

if TYPE_CHECKING:
    from loguru._handler import Message

    from src.schemas.tasks import TaskBase


class ThreadedTaskHandler:

    def __init__(self, queue: "InternalQueue[List[Union[dict, str]]]"):
        self.queue = queue

    def write(self, message: "Message"):
        record = LogRecord(**message.record)
        task: Optional["TaskBase"] = record.extra.get("task")

        ReprManager.push_repr_item_to_thread_items(record, thread=th.get_ident())

        if task is not None and task.task_status in [
            enums.TaskStatus.FAILED,
            enums.TaskStatus.SUCCESS,
            enums.TaskStatus.SKIPPED,
        ]:
            self.queue.put(ReprManager.get_thread_repr_items(), block=True)
            ReprManager.delete_thread_repr_items()
