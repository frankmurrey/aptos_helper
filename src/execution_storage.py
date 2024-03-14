from typing import Optional, Dict
from uuid import UUID


class ExecutionStorage:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ExecutionStorage, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.__pre_execution_data: Dict[str, dict] = {}

    @property
    def pre_execution_data(self) -> Dict[str, dict]:
        return self.__pre_execution_data

    def get_by_wallet_id_and_task_id(
            self,
            wallet_id: UUID,
            task_id: UUID
    ) -> Optional[dict]:
        return self.__pre_execution_data.get(f"{wallet_id}_{task_id}")

    def set_pre_execution_data(
            self,
            wallet_id: UUID,
            task_id: UUID,
            data: dict
    ):
        self.__pre_execution_data[f"{wallet_id}_{task_id}"] = data

