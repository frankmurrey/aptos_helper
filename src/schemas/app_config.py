from typing import Union

from pydantic import BaseModel


class AppConfigSchema(BaseModel):
    preserve_logs: bool = True
    mobile_proxy_rotation: bool = False
    mobile_proxy_rotation_link: Union[str, None] = ""
    aptos_rpc_url: str = "https://rpc.ankr.com/http/aptos/v1"
