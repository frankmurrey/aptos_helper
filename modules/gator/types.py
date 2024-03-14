from pydantic import BaseModel
from typing import List


class MarketData(BaseModel):
    asks: List[int]
    base_available: int
    base_ceiling: int
    base_total: int
    bids: List[int]
    custodian_id: str
    market_id: str
    quote_available: int
    quote_ceiling: int
    quote_total: int
