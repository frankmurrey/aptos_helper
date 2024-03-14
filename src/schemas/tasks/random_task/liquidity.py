from pydantic import Field
from modules.random.liquidity import RandomAddLiquidity


from src import enums
from src.schemas.tasks import AddLiquidityTaskBase


class RandomAddLiquidityTask(AddLiquidityTaskBase):
    module_name = enums.ModuleName.RANDOM
    module_type = enums.ModuleType.SWAP
    module = Field(default=RandomAddLiquidity)