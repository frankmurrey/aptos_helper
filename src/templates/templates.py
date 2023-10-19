import os

from loguru import logger

from src.templates._tokens_template import TOKENS_DATA
from src.templates._app_config_template import APP_CONFIG
from src.file_manager import FileManager

from src import paths


class Templates:
    def __init__(self):
        self.file_manager = FileManager()
        self.all_temp_files = paths.TempFiles().__dict__

    def get_non_existent_temp_files(self):
        """
        Returns a list of file paths for temporary files that do not exist.

        Returns:
            List[str]: list: A list of file paths (strings) for temporary files that do not exist.
            If all temporary files exist, an empty list is returned.
        """
        not_found_files = []
        for file_name, file_path in self.all_temp_files.items():
            if not os.path.exists(file_path):
                not_found_files.append(file_path)

        if not_found_files:
            return not_found_files

        return []

    def create_not_found_temp_files(self):
        file_paths = self.get_non_existent_temp_files()
        if not file_paths:
            return

        for file_path in file_paths:
            if file_path.endswith('tokens.json'):
                self.create_tokens_json_file(file_path=file_path)

            if file_path.endswith('app_config.json'):
                self.create_app_config_json_file(file_path=file_path)

            if file_path.endswith('logs'):
                os.mkdir(file_path)
                logger.info(f'Created {file_path} directory\n')

        logger.critical('Temp files created, restart me please')
        exit(1)

    def create_tokens_json_file(self, file_path):
        data = TOKENS_DATA
        self.file_manager.write_data_to_json_file(file_path=file_path,
                                                  data=data)
        logger.info(f'Created {file_path} file')

    def create_app_config_json_file(self, file_path):
        data = APP_CONFIG
        self.file_manager.write_data_to_json_file(file_path=file_path,
                                                  data=data)
        logger.info(f'Created {file_path} file')