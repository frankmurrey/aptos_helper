import json
import time
from typing import Union, TYPE_CHECKING

import websocket
from aptos_sdk.account import Account
from loguru import logger

from modules.base import SingleCoinModuleBase
from modules.merkle import types
from modules.merkle.math import calculate_market_price

if TYPE_CHECKING:
    from src.schemas.tasks import MerklePlaceCancelOrderTask
    from src.schemas.tasks import MerklePlaceOpenOrderTask
    from src.schemas.wallet_data import WalletData


class MerkleModuleBase(SingleCoinModuleBase):
    MIN_PAY_USD = 300

    REF_ADDR = "0x83011465ec892aeed8d7747ac109bb61621d08b2286a58095617ba117e980832"
    LONG_FEE_PERCENT = 7
    SHORT_FEE_PERCENT = 13

    SHORT_POSITIONS = "0x77754267bccc4f8e8e8a8d212a8a275e8406b60faf9a337445e47de38223bf30"
    LONG_POSITIONS = "0x97fa74193613f09ad556b2d78b10aedcf34f2b7b53dd607fffd528096def1dcf"

    def __init__(
            self,
            account: Account,
            task: Union['MerklePlaceOpenOrderTask', 'MerklePlaceCancelOrderTask'],
            base_url: str,
            wallet_data: 'WalletData',
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies,
            wallet_data=wallet_data
        )

        self.router_address = self.get_address_from_hex(
            "0x5ae6789dd2fec1a9ec9cccfb3acaf12e93d432f0a3a42c92fe1a9d490b7bbc06"
        )
        self._ws_url = "wss://api.prod.merkle.trade/v1"

    def get_apt_price(self) -> Union[float, None]:
        ws = websocket.WebSocket()
        sub_msg_0 = f'{{"type":"sub","key":"account:{self.account.address().hex()}:position_events"}}'
        sub_msg_1 = f'{{"type":"sub","key":"price:APT_USD"}}'

        try:
            ws.connect(self._ws_url)
            ws.send(sub_msg_0)
            time.sleep(0.1)
            ws.send(sub_msg_1)

            while True:
                result = ws.recv()
                result_json = json.loads(result)
                if result_json.get("data"):
                    return float(result_json.get("data").get("price"))

                time.sleep(1)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

        finally:
            ws.close()

    def get_pair_info(self) -> Union[types.PairInfo, None]:
        try:
            ra = self.router_address.hex()
            res_type = f"{ra}::trading::PairInfo<{ra}::pair_types::APT_USD, {self.coin_x.contract_address}>"
            resource = self.client.account_resource(
                self.router_address.hex(),
                res_type
            )
            return types.PairInfo(**resource["data"])

        except Exception as e:
            logger.error(f"Error getting pair info: {e}")
            return None

    def get_pair_state(self) -> Union[types.PairState, None]:
        try:
            ra = self.router_address.hex()
            res_type = f"{ra}::trading::PairState<{ra}::pair_types::APT_USD, {self.coin_x.contract_address}>"
            resource = self.client.account_resource(
                self.router_address.hex(),
                res_type
            )
            return types.PairState(**resource["data"])

        except Exception as e:
            logger.error(f"Error getting pair state: {e}")
            return None

    def get_market_apt_price(
            self,
            pair_info: types.PairInfo,
            pair_state: types.PairState
    ) -> Union[float, None]:
        """
        Get the market price of APT
        Returns:

        """
        price_decimals = self.get_apt_price()
        if price_decimals is None:
            logger.error("Error getting price")
            return None

        market_price = calculate_market_price(
            price_decimals=price_decimals,
            long_open_interest=pair_state.long_open_interest,
            short_open_interest=pair_state.short_open_interest,
            skew_factor=pair_info.skew_factor
        )

        return market_price


