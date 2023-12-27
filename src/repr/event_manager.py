import threading as th
from typing import List, Union

from loguru import logger

from src.schemas.logs import LogRecord
from src.internal_queue import InternalQueue


def state_setter(obj: "ReprEventManager", state: dict):
    obj.queue = state["queue"]


class ReprEventManager:
    def __init__(self):
        self.queue = InternalQueue[List[Union[LogRecord, str]]]()

    @staticmethod
    def patch_log(
            actual_record: dict,
            received_record: dict,
    ):
        # TODO: maybe move to repr manager
        actual_record.update(received_record)

    def loop(self):

        while True:
            repr_items = self.queue.get(block=True)

            for item in repr_items:
                if isinstance(item, LogRecord):
                    (
                        logger
                        .patch(lambda actual_record: self.patch_log(actual_record, item.dict()))
                        .log(item.level.name, item.message)
                    )
                elif isinstance(item, str):
                    print(item)
                else:
                    raise ValueError(f"Unexpected repr item type: {type(item)}")

    def start(self):
        thread = th.Thread(target=self.loop, name="log_event_manager")
        thread.start()

    def __reduce__(self):
        return (
            object.__new__,
            (type(self),),
            {
                "queue": self.queue
            },
            None,
            None,
            state_setter,
        )


repr_event_manager = ReprEventManager()
