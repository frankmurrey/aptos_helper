import time
import random

from typing import Union, List
from datetime import datetime, timedelta

from src.file_manager import FileManager
from src.config_manager import print_config
from src.proxy_manager import ProxyManager
from src.schemas.wallet_data import WalletData
from src.storage import Storage
from src.templates.templates import Templates
from src.action_logger import log_all_actions_to_xlsx

from modules.pancake.swap import PancakeSwap
from modules.liquidity_swap.swap import Swap

from modules.the_aptos_bridge.bridge import AptosBridge
from modules.the_aptos_bridge.claim import BridgedTokenClaimer

from modules.abel_finance.mint_redeem import AbleFinance

from modules.thala.liquidity import Thala
from modules.liquidity_swap.liquidity import Liquidity as LSLiquidity

from modules.delegation.delegate import Delegate
from modules.delegation.unlock import Unlock

from src.utils.balance_checker import BalanceChecker, write_balance_data_to_xlsx

from loguru import logger
from aptos_sdk.account import Account


class ModuleExecutor:
    file_manager: FileManager
    wallets: List[WalletData]

    def __init__(self, config):
        self.config = config
        self.module_name = config.module_name
        self.storage = Storage()
        self.app_config = self.storage.get_app_config()
        self.wallets = self.storage.get_wallets_data()
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

        if self.storage.get_shuffle_wallets() is True:
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
                                                       base_url=self.storage.get_rpc_url())

            if self.config.test_mode is True and index == 2:
                logger.info(f"Process finished in Test Mode\n")
                break

            if index == wallets_amount - 1:
                if self.config.module_name == "balance_checker":
                    data = self.storage.get_wallet_balances()
                    f_path = self.config.file_path
                    write_balance_data_to_xlsx(data=data,
                                               path=f_path,
                                               coin_option=self.config.coin_option)

                if self.app_config.preserve_logs is True:
                    log_all_actions_to_xlsx()

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
        proxy_data = wallet_data.proxy
        proxy_manager = ProxyManager(proxy_data=proxy_data)
        proxies = proxy_manager.get_proxy()

        if proxy_data:
            if proxy_data.is_mobile is True and self.app_config.mobile_proxy_rotation is True:
                rotation_link = self.app_config.mobile_proxy_rotation_link
                if not rotation_link:
                    logger.error(f"Mobile proxy rotation link is not set (go to app_config.json)")
                    return False
                rotate_status = proxy_manager.rotate_mobile_proxy(rotation_link)
                if rotate_status is False:
                    return False

            current_ip = proxy_manager.get_ip()
            if current_ip is None:
                logger.error(f"Proxy {wallet_data.proxy.host}:{wallet_data.proxy.port} is not valid or bad auth params")
                return False
            else:
                logger.info(f"Proxy valid, using {wallet_data.proxy.host}:{wallet_data.proxy.port} (ip: {current_ip})")

        if self.module_name == 'pancake':
            pancake = PancakeSwap(base_url=base_url,
                                  config=self.config,
                                  proxies=proxies)
            swap_status = pancake.make_swap(private_key=wallet_data.wallet)
            execution_status = swap_status

        elif self.module_name == "aptos_bridge_claim":
            claimer = BridgedTokenClaimer(base_url=base_url,
                                          config=self.config,
                                          proxies=proxies)
            claim_status = claimer.claim_batch(private_key=wallet_data.wallet)
            execution_status = claim_status

        elif self.module_name == "aptos_bridge":
            bridge = AptosBridge(base_url=base_url,
                                 config=self.config,
                                 proxies=proxies)
            bridge_status = bridge.send_transaction(private_key=wallet_data.wallet,
                                                    receiver_address=wallet_data.evm_pair_address)
            execution_status = bridge_status

        elif self.module_name == "able_mint":
            mint = AbleFinance(base_url=base_url,
                               config=self.config,
                               proxies=proxies)
            mint_status = mint.send_mint_transaction(private_key=wallet_data.wallet)
            execution_status = mint_status

        elif self.module_name == "able_redeem":
            redeem = AbleFinance(base_url=base_url,
                                 config=self.config,
                                 proxies=proxies)
            redeem_status = redeem.send_redeem_transaction(private_key=wallet_data.wallet)
            execution_status = redeem_status

        elif self.module_name == "thala_add_liquidity":
            thala = Thala(base_url=base_url,
                          config=self.config,
                          proxies=proxies)
            add_liq_status = thala.send_add_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = add_liq_status

        elif self.module_name == "thala_remove_liquidity":
            thala = Thala(base_url=base_url,
                          config=self.config,
                          proxies=proxies)
            remove_liq_status = thala.send_remove_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = remove_liq_status

        elif self.module_name == "liquidityswap_swap":
            liq_swap = Swap(base_url=base_url,
                            config=self.config,
                            proxies=proxies)

            swap_status = liq_swap.make_swap(private_key=wallet_data.wallet)
            execution_status = swap_status

        elif self.module_name == "liquidityswap_add_liquidity":
            liq_swap = LSLiquidity(base_url=base_url,
                                   config=self.config,
                                   proxies=proxies)
            add_liq_status = liq_swap.send_add_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = add_liq_status

        elif self.module_name == "liquidityswap_remove_liquidity":
            liq_swap = LSLiquidity(base_url=base_url,
                                   config=self.config,
                                   proxies=proxies)
            remove_liq_status = liq_swap.send_remove_liquidity_transaction(private_key=wallet_data.wallet)
            execution_status = remove_liq_status

        elif self.module_name == "delegate":
            delegate = Delegate(base_url=base_url,
                                config=self.config,
                                proxies=proxies)
            delegate_status = delegate.send_delegation_transaction(private_key=wallet_data.wallet)
            execution_status = delegate_status

        elif self.module_name == "unlock":
            unlock = Unlock(base_url=base_url,
                            config=self.config,
                            proxies=proxies)
            unlock_status = unlock.send_unlock_transaction(private_key=wallet_data.wallet)
            execution_status = unlock_status

        elif self.module_name == "balance_checker":
            balance_checker = BalanceChecker(base_url=base_url,
                                             config=self.config,
                                             proxies=proxies)
            address = Account.load_key(wallet_data.wallet).address()
            balance_status = balance_checker.get_balance_decimals(address=address)

            if balance_status is not None:
                action_status = True
            else:
                action_status = False

            self.storage.append_wallet_balance({address.hex(): balance_status})

            execution_status = action_status

        return execution_status

