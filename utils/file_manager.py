import os
import json
import pickle
from typing import Union, List, Dict, Any
from datetime import datetime

import csv
import numpy as np
import pandas as pd
from loguru import logger

from src import paths
from src import exceptions
from utils.misc import detect_separator


class FileManager:

    def __init__(self):
        pass

    @staticmethod
    def save_to_pickle_file(data, file_path):
        if not file_path:
            return None
        try:
            with open(file_path, "wb") as file:
                pickle.dump(data, file)

        except Exception as e:
            logger.error(f"Error while writing file \"{file_path}\": {e}")
            return None

    @staticmethod
    def read_from_pickle_file(file_path):
        try:
            with open(file_path, "rb") as file:
                return pickle.load(file)

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            return None

    @staticmethod
    def read_abi_from_file(file_path: str) -> Union[dict, list, None]:
        # TODO: possibly excessive method

        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                return json.loads(file.read())

        except json.decoder.JSONDecodeError as e:
            logger.error(f"File \"{filename}\" is not a valid JSON file")

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            return None

    @staticmethod
    def read_data_from_json_file(file_path) -> Union[dict, None]:
        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                return json.load(file)

        except json.decoder.JSONDecodeError as e:
            logger.error(f"File \"{filename}\" is not a valid JSON file")

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            return None

        return None

    @staticmethod
    def read_data_from_txt_file(file_path: str) -> Union[List[str], None]:
        filename = os.path.basename(file_path)

        if not os.path.exists(file_path):
            logger.error(f"File \"{filename}\" does not exist")
            return None

        try:
            with open(file_path, "r") as file:
                data = file.read().splitlines()
                return data

        except Exception as e:
            logger.error(f"Error while reading file \"{file_path}\": {e}")
            return None

    @staticmethod
    def read_data_from_csv_file(
            filepath: str
    ) -> Union[List[Dict[str, Any]], None]:
        separator = detect_separator(filepath, [",", ";"])
        if separator is None:
            logger.error(f"Could not detect separator in file \"{filepath}\"")
            return None

        df = pd.read_csv(filepath, sep=separator)
        df = df.replace(np.nan, None)
        return df.to_dict(orient="records")

    @staticmethod
    def get_wallets_from_files():
        raise NotImplementedError

    @staticmethod
    def write_data_to_json_file(
            file_path: str,
            data: Union[dict, list],
            raise_exception: bool = False
    ) -> None:
        if not file_path:
            return None
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4, default=str)

        except Exception as e:
            logger.error(f"Error while writing file \"{file_path}\": {e}")
            if raise_exception:
                raise exceptions.AppValidationError(f"Error while writing file \"{file_path}\": {e}")

    @staticmethod
    def create_new_logs_dir(dir_name_suffix=None):
        if os.path.exists(paths.LOGS_DIR) is False:
            os.mkdir(paths.LOGS_DIR)
            logger.info(f"Creating logs dir in \"{paths.LOGS_DIR}\"")

        date_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if dir_name_suffix:
            dir_name = f"log_{dir_name_suffix}_{date_time}"
        else:
            dir_name = f"log_{date_time}"

        new_logs_dir = f"{paths.LOGS_DIR}\\{dir_name}"
        os.mkdir(new_logs_dir)

        if not os.path.exists(new_logs_dir):
            return
        return new_logs_dir

    @staticmethod
    def write_data_to_csv(path,
                          data: List[List[str]],
                          mode: str = "w",):
        if not os.path.exists(os.path.dirname(path)):
            logger.error(f"Path \"{os.path.dirname(path)}\" does not exist")
            return

        with open(path, mode, newline='') as file:
            writer = csv.writer(file)
            for row in data:
                writer.writerow(row)

    @staticmethod
    def write_data_to_txt_file(
            file_path: str,
            data: Union[str, list],
            raise_exception: bool = False
    ) -> None:
        if not file_path:
            return
        try:
            with open(file_path, "w") as file:
                if isinstance(data, list):
                    for line in data:
                        file.write(f"{line}\n")
                else:
                    file.write(data)

        except Exception as e:
            logger.error(f"Error while writing file \"{file_path}\": {e}")
            if raise_exception:
                raise exceptions.AppValidationError(f"Error while writing file \"{file_path}\": {e}")