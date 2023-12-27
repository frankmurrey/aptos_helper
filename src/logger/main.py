from loguru import logger
from sys import stdout

import config


def configure_logger():
    logger.remove()
    logger.add(
        stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{line: <3}</cyan> - <level>{message}</level>"
        ),
        level=config.LOGGING_LEVEL
    )
