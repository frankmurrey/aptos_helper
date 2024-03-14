from typing import List, Union
from typing import TYPE_CHECKING

from loguru import logger

from src.logger.handlers import ThreadedTaskHandler
import config

if TYPE_CHECKING:
    from src.internal_queue import InternalQueue


def configure_threaded_task_executor_logger(queue: "InternalQueue[List[Union[dict, str]]]"):
    logger.remove()
    logger.configure(
        handlers=[{
            "sink": ThreadedTaskHandler(queue),
            "level": config.LOGGING_LEVEL,
            "format": (
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{line: <3}</cyan> - <level>{message}</level>"
            ),
        }],
        extra={"task": None}
    )
