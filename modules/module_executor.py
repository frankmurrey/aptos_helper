import time
import random

from typing import Union, List
from datetime import datetime, timedelta

from src.file_manager import FileManager
from src.config_manager import print_config
from src.proxy_manager import ProxyManager
from src.schemas.wallet_data import WalletData
from src.storage import WalletsStorage
from src.templates.templates import Templates

from modules.pancake.swap import PancakeSwap
from modules.liquidity_swap.swap import LiquiditySwap


from modules.the_aptos_bridge.bridge import AptosBridge
from modules.the_aptos_bridge.claim import BridgedTokenClaimer

from modules.abel_finance.mint_redeem import AbleFinance

from modules.thala.liquidity import Thala

from loguru import logger
from aptos_sdk.account import Account


class ModuleExecutor:
    file_manager: FileManager
    proxy_manager: ProxyManager
    wallets: List[WalletData]

    def __init__(self, config):
        self.proxy_manager = ProxyManager()
        self.config = config
        self.module_name = config.module_name
        self.wallets_storage = WalletsStorage()
        self.wallets = self.wallets_storage.get_wallets_data()
        self.templates = Templates()

    def get_delay_sec(self, execution_status: bool) -> int:
        if execution_status is True:
            return random.randint(self.config.min_delay_sec, self.config.max_delay_sec)

        return 3

    def blur_private_key(self, private_key: str) -> str:
        length = len(private_key)
        start_index = length // 10
        end_index = length - start_index
        blurred_private_key = private_key[:start_index] + '*' * (end_index - start_index) + private_key[end_index + 4:]
        return blurred_private_key

    def start(self):
        print_config(config=self.config)

        if self.wallets_storage.get_shuffle_wallets() is True:
            wallets = self.wallets
            random.shuffle(wallets)
        else:
            wallets = self.wallets

        wallets_amount = len(wallets)
        for index, wallet_data in enumerate(self.wallets):
            wallet_address = Account.load_key(wallet_data.wallet).address()
            logger.info(f"[{index + 1}] - {wallet_address}")
            logger.info(f"PK - {self.blur_private_key(wallet_data.wallet)}")

            execute_status: bool = self.execute_module(wallet_data=wallet_data,
                                                       base_url=self.wallets_storage.get_rpc_url())

            if index == wallets_amount - 1:
                logger.info(f"Process is finished\n")
                break

            time_delay_sec = self.get_delay_sec(execution_status=execute_status)

            delta = timedelta(seconds=time_delay_sec)
            result_datetime = datetime.now() + delta

            logger.info(f"Waiting {time_delay_sec} seconds, next wallet {result_datetime}\n")
            time.sleep(time_delay_sec)

    def execute_module(self,
                       wallet_data: WalletData,
                       base_url: str) -> Union[bool, None]:

        execution_status = None
        proxy: dict = self.proxy_manager.get_proxy(proxy_data=wallet_data.proxy)
        if proxy:
            is_proxy_valid = self.proxy_manager.ping(proxy=proxy)
            if is_proxy_valid is False:
                logger.error(f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params")
                return False
            else:
                logger.info(f"Proxy valid, using {wallet_data.proxy.host}:{wallet_data.proxy.port}")

        if self.module_name == 'pancake':
            pancake = PancakeSwap(base_url=base_url,
                                  config=self.config,
                                  proxies=proxy)
            swap_status = pancake.make_swap(private_key=wallet_data.wallet)
            execution_status = swap_status

        elif self.module_name == "aptos_bridge_claim":
            claimer = BridgedTokenClaimer(base_url=base_url,
                                          config=self.config,
                                          proxies=proxy)
            claim_status = claimer.claim_batch(private_key=wallet_data.wallet)
            execution_status = claim_status

        elif self.module_name == "aptos_bridge":
            bridge = AptosBridge(base_url=base_url,
                                 config=self.config,
                                 proxies=proxy)
            bridge_status = bridge.send_transaction(private_key=wallet_data.wallet,
                                                    receiver_address=wallet_data.evm_pair_address)
            execution_status = bridge_status

        elif self.module_name == "able_mint":
            mint = AbleFinance(base_url=base_url,
                               config=self.config,
                               proxies=proxy)
            mint_status = mint.send_mint_transaction(private_key=wallet_data.wallet)
            execution_status = mint_status

        elif self.module_name == "able_redeem":
            redeem = AbleFinance(base_url=base_url,
                                 config=self.config,
                                 proxies=proxy)
            redeem_status = redeem.send_redeem_transaction(private_key=wallet_data.wallet)
            execution_status = redeem_status

        elif self.module_name == "thala_add_liquidity":
            thala = Thala(base_url=base_url,
                          config=self.config,
                          proxies=proxy)
            add_liq_status = thala.send_add_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = add_liq_status

        elif self.module_name == "thala_remove_liquidity":
            thala = Thala(base_url=base_url,
                          config=self.config,
                          proxies=proxy)
            remove_liq_status = thala.send_remove_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = remove_liq_status

        elif self.module_name == "liquidityswap_swap":
            liq_swap = LiquiditySwap(base_url=base_url,
                                     config=self.config,
                                     proxies=proxy)

            swap_status = liq_swap.make_swap(private_key=wallet_data.wallet)
            execution_status = swap_status

        return execution_status

