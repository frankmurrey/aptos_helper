from dataclasses import dataclass, asdict
from datetime import datetime
from datetime import timedelta
from typing import Optional, Dict, Union
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel

from src import enums

if TYPE_CHECKING:
    from loguru._recattrs import RecordFile
    from loguru._recattrs import RecordLevel
    from loguru._recattrs import RecordProcess
    from loguru._recattrs import RecordThread


class WalletActionSchema(BaseModel):
    module_name: enums.ModuleName = None
    module_type: enums.ModuleType = None

    date_time: str = None
    wallet_address: str = None
    proxy: Union[str, None] = None
    is_success: Union[bool, None] = None
    transaction_hash: str = None

    status: str = None
    traceback: str = None

    def set_error(self, message: str):
        logger.error(message)
        self.status = message
        self.is_success = False


@dataclass
class LogRecord:
    elapsed: timedelta
    exception: Optional[Exception]
    extra: Dict
    file: "RecordFile"
    function: str
    level: "RecordLevel"
    line: int
    message: str
    module: str
    name: str
    process: "RecordProcess"
    thread: "RecordThread"
    time: datetime

    def dict(self):
        return asdict(self)
