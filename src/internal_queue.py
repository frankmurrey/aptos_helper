from queue import Empty
import multiprocessing as mp
import multiprocessing.queues as mpq
from typing import Union, TypeVar, List, Generic

_T = TypeVar('_T')


class InternalQueue(
    mpq.Queue,
    Generic[_T]
):
    """
    An extension of the multiprocessing.Queue class with additional methods for non-blocking operations.
    This class inherits from multiprocessing.queues.Queue and provides some additional methods.
    """
    def __init__(self, *args, **kwargs):
        ctx = mp.get_context()
        super().__init__(*args, **kwargs, ctx=ctx)

    def get_or_none(self) -> Union[_T, None]:
        """
        Remove and return an item from the queue without blocking.
        Only get an item if one is immediately available. Otherwise get None.
        """
        try:
            return super().get_nowait()
        except Empty:
            return None

    def get_all(self) -> List[_T]:
        """
        Remove and return all items from the queue without blocking.
        """
        items = []
        try:
            while True:
                items.append(self.get_nowait())
        except Empty:
            pass
        return items

    def clear(self):
        """
        Remove all items from the queue.
        """
        try:
            while True:
                self.get_nowait()
        except Empty:
            pass