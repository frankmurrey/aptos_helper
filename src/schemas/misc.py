from typing import Optional

from pydantic import BaseModel


class EntryFunctionPayloadData(BaseModel):
    address: str
    func_name: str
    type_args: list
    args: list
