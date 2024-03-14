from pydantic import BaseModel


class PairInfo(BaseModel):
    execute_time_limit: int
    execution_fee: int
    liquidate_threshold: int
    maker_fee: int
    market_depth_above: int
    market_depth_below: int
    max_funding_velocity: int
    max_leverage: int
    max_open_interest: int
    maximum_position_collateral: int
    maximum_profit: int
    min_leverage: int
    minimum_order_collateral: int
    minimum_position_collateral: int
    minimum_position_size: int
    paused: bool
    rollover_fee_per_timestamp: int
    skew_factor: int
    taker_fee: int


class PositionHandle(BaseModel):
    handle: str


class PairState(BaseModel):
    acc_funding_fee_per_size: int
    acc_funding_fee_per_size_positive: bool
    acc_rollover_fee_per_collateral: int
    funding_rate: int
    funding_rate_positive: bool
    last_accrue_timestamp: int
    long_open_interest: int
    long_positions: PositionHandle
    next_order_id: int
    orders: PositionHandle
    short_open_interest: int
    short_positions: PositionHandle


class UserPosition(BaseModel):
    acc_funding_fee_per_size: int
    acc_funding_fee_per_size_positive: bool
    acc_rollover_fee_per_collateral: int
    avg_price: int
    collateral: int
    last_execute_timestamp: int
    size: int
    stop_loss_trigger_price: int
    take_profit_trigger_price: int
    uid: int
