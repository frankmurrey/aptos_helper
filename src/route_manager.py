from src.schemas.pancake import PancakeConfigSchema
from src.schemas.aptos_bridge import AptosBridgeConfigSchema
from src.schemas.able_finance import (AbleMintConfigSchema,
                                      AbleRedeemConfigSchema)
from src.schemas.thala import (ThalaAddLiquidityConfigSchema,
                               ThalaRemoveLiquidityConfigSchema)

from loguru import logger


class RouteManagerBase:
    def is_valid_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def is_valid_int(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def is_positive(self, value):
        return value > 0

    def is_less_than(self, value, max_value):
        return value < max_value


class RouteManagerTransferTypeBase(RouteManagerBase):
    def __init__(self, config):
        self.config = config

    def check_amount_out(self):
        min_out = self.config.min_amount_out
        max_out = self.config.max_amount_out

        if self.config.send_all_balance is False:
            if not min_out or not max_out:
                error_msg = f"Min/max amount out should be specified"
                return error_msg

            if not self.is_valid_float(min_out) or not self.is_valid_float(max_out):
                error_msg = f"Min/max amount out should be a number (float)"
                return error_msg

            if not self.is_positive(float(min_out)) or not self.is_positive(float(max_out)):
                error_msg = f"Min/max amount out should be positive"
                return error_msg

            if float(min_out) > float(max_out):
                error_msg = f"Min amount out should be less than max amount out or equal"
                return error_msg

        return True

    def check_gas_price(self):
        if not self.config.gas_price:
            error_msg = f"Gas price should be specified"
            return error_msg

        if not self.is_valid_float(self.config.gas_price):
            error_msg = f"Gas price should be a number (float)"
            return error_msg

        if not self.is_positive(float(self.config.gas_price)):
            error_msg = f"Gas price should be positive"
            return error_msg

        return True

    def check_gas_limit(self):
        if not self.config.gas_limit:
            error_msg = f"Gas limit should be specified"
            return error_msg

        if not self.is_valid_int(self.config.gas_limit):
            error_msg = f"Gas limit should be a number (int)"
            return error_msg

        if not self.is_positive(float(self.config.gas_limit)):
            error_msg = f"Gas limit should be positive"
            return error_msg

        return True

    def check_delay(self):
        min_delay = self.config.min_delay_sec
        max_delay = self.config.max_delay_sec

        if not self.is_valid_int(min_delay) or not self.is_valid_int(max_delay):
            error_msg = f"Min/max delay should be a number (int)"
            return error_msg

        if not self.is_positive(float(min_delay)) or not self.is_positive(float(max_delay)):
            error_msg = f"Min/max delay should be positive"
            return error_msg

        if float(min_delay) > float(max_delay):
            error_msg = f"Min delay should be less or equal to max delay"
            return error_msg

        return True

    def check_txn_timeout(self):
        if self.config.wait_for_receipt is True:
            if not self.is_valid_int(self.config.txn_wait_timeout_sec):
                error_msg = f"Transaction deadline should be a number (int)"
                return error_msg

            if not self.is_positive(float(self.config.txn_wait_timeout_sec)):
                error_msg = f"Transaction deadline should be positive"
                return error_msg

        return True

    def validate(self):

        status_amount_out = self.check_amount_out()
        if status_amount_out is not True:
            return status_amount_out

        status_gas_price = self.check_gas_price()
        if status_gas_price is not True:
            return status_gas_price

        status_gas_limit = self.check_gas_limit()
        if status_gas_limit is not True:
            return status_gas_limit

        status_delay = self.check_delay()
        if status_delay is not True:
            return status_delay

        status_txn_timeout = self.check_txn_timeout()
        if status_txn_timeout is not True:
            return status_txn_timeout

        return True


class SwapRouteValidator(RouteManagerTransferTypeBase):
    config: PancakeConfigSchema

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def check_slippage(self):
        if not self.config.slippage:
            error_msg = f"Slippage should be specified"
            return error_msg

        if not self.is_valid_float(self.config.slippage):
            error_msg = f"Slippage should be a number (float)"
            return error_msg

        if not self.is_positive(float(self.config.slippage)):
            error_msg = f"Slippage should be positive"
            return error_msg

        return True

    def check_token_pair(self):
        if self.config.coin_to_swap == self.config.coin_to_receive:
            error_msg = f"'Coin to swap' and 'Coin to receive' should be different"
            return error_msg

        return True

    def check_is_route_valid(self):
        status_token_pair = self.check_token_pair()
        if status_token_pair is not True:
            return status_token_pair

        base_validation_status = self.validate()
        if base_validation_status is not True:
            return base_validation_status

        status_slippage = self.check_slippage()
        if status_slippage is not True:
            return status_slippage

        return True


class AptosBridgeRouteValidator(RouteManagerTransferTypeBase):
    config: AptosBridgeConfigSchema

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def check_coin_bridge(self):
        if not self.config.coin_to_bridge:
            error_msg = f"Coin bridge should be specified"
            return error_msg

        return True

    def check_dst_chain(self):
        if not self.config.dst_chain_name:
            error_msg = f"Destination chain should be specified"
            return error_msg

        return True

    def check_is_route_valid(self):
        status_coin_bridge = self.check_coin_bridge()
        if status_coin_bridge is not True:
            return status_coin_bridge

        status_dst_chain = self.check_dst_chain()
        if status_dst_chain is not True:
            return status_dst_chain

        base_validation_status = self.validate()
        if base_validation_status is not True:
            return base_validation_status

        return True


class AptosBridgeClaimConfigValidator(RouteManagerTransferTypeBase):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def check_is_route_valid(self):
        status_gas_price = self.check_gas_price()
        if status_gas_price is not True:
            return status_gas_price

        status_gas_limit = self.check_gas_limit()
        if status_gas_limit is not True:
            return status_gas_limit

        status_delay = self.check_delay()
        if status_delay is not True:
            return status_delay

        status_txn_timeout = self.check_txn_timeout()
        if status_txn_timeout is not True:
            return status_txn_timeout

        return True


class AbleFinanceMintConfigValidator(RouteManagerTransferTypeBase):
    config: AbleMintConfigSchema

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def check_coin_to_mint(self):
        if not self.config.coin_option:
            error_msg = f"Coin to stake should be specified"
            return error_msg

        return True

    def check_is_route_valid(self):
        status_coin_to_mint = self.check_coin_to_mint()
        if status_coin_to_mint is not True:
            return status_coin_to_mint

        base_validation_status = self.validate()
        if base_validation_status is not True:
            return base_validation_status

        return True


class AbleFinanceRedeemConfigValidator(RouteManagerTransferTypeBase):
    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def check_is_route_valid(self):
        status_gas_price = self.check_gas_price()
        if status_gas_price is not True:
            return status_gas_price

        status_gas_limit = self.check_gas_limit()
        if status_gas_limit is not True:
            return status_gas_limit

        status_delay = self.check_delay()
        if status_delay is not True:
            return status_delay

        status_txn_timeout = self.check_txn_timeout()
        if status_txn_timeout is not True:
            return status_txn_timeout

        return True


class ThalaAddLiquidityConfigValidator(RouteManagerTransferTypeBase):
    config: ThalaAddLiquidityConfigSchema

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def coins_option_check(self):
        if not self.config.coin_x or not self.config.coin_y:
            error_msg = f"Coin X and Y should be specified"
            return error_msg

        return True

    def check_is_route_valid(self):
        status_coin_option = self.coins_option_check()
        if status_coin_option is not True:
            return status_coin_option

        base_validation_status = self.validate()
        if base_validation_status is not True:
            return base_validation_status

        return True


class ThalaRemoveLiquidityConfigValidator(RouteManagerTransferTypeBase):
    config: ThalaRemoveLiquidityConfigSchema

    def __init__(self, config):
        super().__init__(config)
        self.config = config

    def coins_option_check(self):
        if not self.config.coin_x or not self.config.coin_y:
            error_msg = f"Coin X and Y should be specified"
            return error_msg

        return True

    def check_is_route_valid(self):
        status_coin_option = self.coins_option_check()
        if status_coin_option is not True:
            return status_coin_option

        base_validation_status = self.validate()
        if base_validation_status is not True:
            return base_validation_status

        return True











