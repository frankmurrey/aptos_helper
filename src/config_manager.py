import os
import time

from typing import Union
from sys import stderr

from src.paths import CONFIG_DIR

import yaml

from pydantic import BaseModel
from loguru import logger


def print_config(config):
    delay_seconds = 2

    logger.remove()
    logger.add(stderr,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{line: <3}</cyan>"
                      " - <level>{message}</level>")
    logger.info(f'Config:')
    for key, value in config.__dict__.items():
        logger.warning(f'{key}: {value}')

    logger.info(f"Starting in ({delay_seconds}) seconds")
    logger.info("Press 'Ctrl+C' to stop the process\n")
    logger.debug('Created by: https://github.com/frankmurrey (tg @shnubjack)\n')
    time.sleep(delay_seconds)


class ConfigManager:
    def __init__(self, config_type):
        self.config_type = config_type
        self.config_obj = config_type()

    def get_file_path(self) -> Union[str, None]:
        try:
            if not issubclass(self.config_type, BaseModel):
                logger.error(f"Config type {self.config_type} is not a subclass of pydantic.BaseModel")
                return None

            module_name = self.config_obj.module_name
            file_path = f"{CONFIG_DIR}\\{module_name}.yaml"

            if not os.path.exists(file_path):
                logger.error(f"Config file {file_path} does not exist")
                return None

            return file_path
        except Exception as e:
            logger.error(f"Error getting config file path: {e}")
            return None

    def save_to_file(self, config_data: dict):
        file_path = self.get_file_path()
        if not file_path:
            return None

        with open(file_path, "w") as file:
            yaml.dump(config_data, file)

    def read_from_file(self) -> Union[dict, None]:
        file_path = self.get_file_path()
        if not file_path:
            return None

        with open(file_path, "r") as file:
            config_data = yaml.load(file, Loader=yaml.FullLoader)
            return config_data

    def get_config_from_file(self):
        config_data = self.read_from_file()
        if not config_data:
            return None

        config = self.config_type(**config_data)
        return config

    def get_config_from_dict(self, config_data: dict):
        config = self.config_type(**config_data)
        return config
