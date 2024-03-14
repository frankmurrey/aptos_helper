import os
from loguru import logger

from src import templates
from utils.file_manager import FileManager

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

    def get_non_matching_temp_files(self):
        """
        Returns a list of file paths for temporary files that do not match the template.

        Returns:
            List[str]: list: A list of file paths (strings) for temporary files that do not match the template.
            If all temporary files match the template, an empty list is returned.
        """
        try:
            non_matching_files = []
            for file_name, file_path in self.all_temp_files.items():

                if file_path.endswith('tokens.json'):
                    data = self.file_manager.read_data_from_json_file(file_path=file_path)

                    if data[0]['default'] != templates.TOKENS_DATA[0]['default']:
                        non_matching_files.append(file_path)

                if file_path.endswith('app_config.json'):
                    data = self.file_manager.read_data_from_json_file(file_path=file_path)

                    data_keys = list(data.keys())
                    template_keys = list(templates.APP_CONFIG.keys())

                    diff_keys = list(set(template_keys) - set(data_keys))
                    if diff_keys:
                        non_matching_files.append(file_path)

            return non_matching_files

        except KeyError:
            self.create_tokens_json_file(file_path=paths.TempFiles().TOKENS_JSON_FILE)

        except Exception as e:
            logger.error(f'Error while comparing temp files with templates: {e}')
            exit(1)

    def create_not_found_temp_files(self):
        not_found_file_paths = self.get_non_existent_temp_files()
        if not not_found_file_paths:
            not_matching_file_paths = self.get_non_matching_temp_files()

            if not_matching_file_paths:
                for file_path in not_matching_file_paths:

                    if file_path.endswith('tokens.json'):
                        self.update_tokens_json_file(file_path=file_path, data=templates.TOKENS_DATA[0]['default'])
                        logger.critical('Tokens file updated, restart me please')

                    if file_path.endswith('app_config.json'):
                        self.update_app_config_json_file(file_path=file_path, data=templates.APP_CONFIG)
                        logger.critical('App config file updated, restart me please')

                    exit(1)

            return

        for file_path in not_found_file_paths:
            if file_path.endswith('tokens.json'):
                self.create_tokens_json_file(file_path=file_path)

            if file_path.endswith('app_config.json'):
                self.create_app_config_json_file(file_path=file_path)

            if file_path.endswith('logs'):
                os.mkdir(file_path)
                logger.info(f'Created {file_path} directory\n')

        logger.critical('Temp files created, restart me please')
        exit(1)

    def update_tokens_json_file(self, file_path: str, data: list):
        try:
            source_data = self.file_manager.read_data_from_json_file(file_path=file_path)
            source_data[0]['default'] = data
            self.file_manager.write_data_to_json_file(file_path=file_path,
                                                      data=source_data)
            logger.info(f'Created {file_path} file')

        except Exception as e:
            logger.error(f'Error while updating {file_path} file: {e}')
            exit(1)

    def update_app_config_json_file(self, file_path: str, data: dict):
        try:
            source_data = self.file_manager.read_data_from_json_file(file_path=file_path)
            dif_keys = list(set(data.keys()) - set(source_data.keys()))
            source_data.update({key: data[key] for key in dif_keys})

            self.file_manager.write_data_to_json_file(file_path=file_path,
                                                      data=source_data)
            logger.info(f'Created {file_path} file')

        except Exception as e:
            logger.error(f'Error while updating {file_path} file: {e}')
            exit(1)

    def create_tokens_json_file(self, file_path):
        data = templates.TOKENS_DATA
        self.file_manager.write_data_to_json_file(file_path=file_path,
                                                  data=data)
        logger.info(f'Created {file_path} file')

    def create_app_config_json_file(self, file_path):
        data = templates.APP_CONFIG
        self.file_manager.write_data_to_json_file(file_path=file_path,
                                                  data=data)
        logger.info(f'Created {file_path} file')