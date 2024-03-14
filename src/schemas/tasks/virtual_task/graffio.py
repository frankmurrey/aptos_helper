from typing import Callable
from pydantic import Field
from pydantic import BaseModel
from pydantic import validator

import config
from src import enums
from src.schemas import validation_mixins
from src.schemas.tasks.base.base import TaskBase
from src.exceptions import AppValidationError
from modules.graffio.draw import GraffioDraw


class GraffioDrawTask(TaskBase):
    module_name: enums.ModuleName = enums.ModuleName.GRAFFIO
    module_type: enums.ModuleType = enums.ModuleType.DRAW
    module: Callable = Field(default=GraffioDraw)

