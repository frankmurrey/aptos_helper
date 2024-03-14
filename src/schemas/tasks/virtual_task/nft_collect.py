from pydantic import Field
from pydantic import validator


from src import enums
from src.schemas.tasks.base.base import TaskBase
from utils import validation
from modules.nft_collect.collect import NftCollect


class NftCollectTask(TaskBase):
    module_name = enums.ModuleName.NFT_COLLECT
    module_type = enums.ModuleType.COLLECT
    module = Field(default=NftCollect)

    min_delay_nft_transfer_sec: float = 1
    max_delay_nft_transfer_sec: float = 2

    @property
    def action_info(self):
        info = f""

        return info

    @validator("min_delay_nft_transfer_sec", pre=True)
    def validate_min_delay_sec_pre(cls, value):
        value = validation.get_converted_to_float(value, "Min Delay")
        value = validation.get_positive(value, "Min Delay")

        return value

    @validator("max_delay_nft_transfer_sec", pre=True)
    def validate_max_delay_sec_pre(cls, value, values):
        value = validation.get_converted_to_float(value, "Max Delay Nft Transfer")
        value = validation.get_greater(value, values["min_delay_nft_transfer_sec"], "Max Delay Nft Transfer")

        return value
