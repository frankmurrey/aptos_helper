from typing import Union

from pydantic import BaseModel


class ProxyData(BaseModel):
    host: str
    port: Union[int, str]
    username: str = None
    password: str = None
    auth: bool = False
    is_mobile: bool = False

    def to_string(self):
        proxy_string = ""
        if self.is_mobile:
            proxy_string += "m$"

        if self.host:
            proxy_string += f"{self.host}"

        if self.port:
            proxy_string += f":{self.port}"

        if self.username and self.password:
            proxy_string += f":{self.username}:{self.password}"

        return proxy_string

