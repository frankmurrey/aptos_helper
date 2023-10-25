import random
import time
from typing import Union, TYPE_CHECKING

from aptos_sdk.account import Account, AccountAddress
from aptos_sdk.transactions import EntryFunction
from aptos_sdk.transactions import Serializer
from aptos_sdk.transactions import TransactionArgument
from aptos_sdk.type_tag import TypeTag
from aptos_sdk.type_tag import StructTag
from aptos_sdk.client import ResourceNotFound
from httpx import ReadTimeout
from loguru import logger

from modules.base import LiquidityModuleBase
from src.schemas.action_models import TransactionPayloadData
from src.schemas.action_models import ModuleExecutionResult
from contracts.tokens.main import Tokens
from src import enums
from utils.delay import get_delay
from modules.thala.math import Math, get_pair_amount_in


if TYPE_CHECKING:
    from src.schemas.tasks import ThalaAddLiquidityTask
    from src.schemas.tasks import ThalaRemoveLiquidityTask


class ThalaLiquidityBase(LiquidityModuleBase):
    base_pool_address = "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::base_pool::Null"
    stable_scripts_address = "0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool_scripts"
    scripts_address = "0x6b3720cd988adeaf721ed9d4730da4324d52364871a68eac62b46d21e4d2fa99::scripts"
    default_lp_stake_pool_id = 7

    def __init__(
            self,
            account: Account,
            task: Union['ThalaAddLiquidityTask', 'ThalaRemoveLiquidityTask'],
            base_url: str,
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies
        )

        self.account = account
        self.task = task

    def get_pools_data(self) -> Union[dict, None]:
        try:
            request_url = "https://app.thala.fi/api/liquidity-pools"
            response = self.client.client.get(url=request_url)
            if response.status_code > 304 or not response.json():
                return None

            return response.json()

        except Exception as e:
            logger.error(f"Error while getting pools data: {e}")
            return None

    def get_pool_for_token_pair(self) -> Union[list, None]:
        pools_data = self.get_pools_data()
        if pools_data is None:
            return None

        pools_data = pools_data.get('data')

        try:
            all_pool_types = []
            for pool in pools_data:
                pool_type = pool.get('poolType')
                if "stable_pool" not in pool_type:
                    continue
                split_pool_type = pool_type.split('<')[1]
                split_pool_type = split_pool_type.split('>')[0]
                split_pool_type = split_pool_type.split(', ')
                if len(split_pool_type) != 4:
                    continue

                all_pool_types.append(split_pool_type)

            for pool_type in all_pool_types:
                double_pool_type = f"{pool_type[0]}, {pool_type[1]}"
                if self.coin_x.contract_address in double_pool_type and self.coin_y.contract_address in double_pool_type:
                    coin_x, coin_y, _, _ = pool_type
                    return pool_type

        except Exception as e:
            logger.error(f"Error while getting pool for token pair: {e}")

        return None

    def get_wallet_lp_balance(
            self,
            account_address: AccountAddress,
            lp_address: str
    ) -> Union[int, None]:
        try:
            wallet_lp_resource = self.client.account_resource(
                account_address,
                f"0x1::coin::CoinStore<{lp_address}>"
            )
            wallet_lp_balance = wallet_lp_resource["data"]["coin"]["value"]

            return wallet_lp_balance

        except Exception as ex:
            logger.error(f"LP not found on wallet balance")
            return None

    def get_liquidity_pool_data(
            self,
            coin_x_address: str,
            coin_y_address: str,
            base_pool_x: str,
            base_pool_y: str
    ) -> Union[dict, None]:
        response_url = "https://app.thala.fi/api/liquidity-pool"
        payload = {
            "pool-type": f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePool"
                         f"<{coin_x_address}, {coin_y_address}, {base_pool_x}, {base_pool_y}>"
        }
        try:
            response = self.client.client.get(
                url=response_url,
                params=payload
            )
        except ReadTimeout:
            logger.error(f"Request timeout")
            return None

        if not response.json():
            return None

        return response.json()


class ThalaAddLiquidity(ThalaLiquidityBase):

    def __init__(
            self,
            account: Account,
            task: 'ThalaAddLiquidityTask',
            base_url: str,
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies
        )

    def get_staked_lp_amount(
            self,
            wallet_address: AccountAddress,
            pool_id: int = None
    ) -> Union[int, None]:
        if not pool_id:
            pool_id = self.default_lp_stake_pool_id

        response_url = f"{self.base_url}view"
        payload = {
            "function": "0x6b3720cd988adeaf721ed9d4730da4324d52364871a68eac62b46d21e4d2fa99"
                        "::farming::stake_and_reward_amount",
            "arguments": [
                str(wallet_address),
                str(pool_id)
            ],
            "type_arguments": [
                "0x7fd500c11216f0fe3095d0c4b8aa4d64a4e2e04f83758462f2b127255643615::thl_coin::THL"
            ]
        }
        response = self.client.post(
            url=response_url,
            json=payload
        )

        if response.status_code != 200:
            return None

        return response.json()

    def get_amount_out_for_token_pair(self) -> Union[dict, None]:
        pool_data = self.get_pool_for_token_pair()
        if pool_data is None:
            base_pool_address_x = self.base_pool_address
            base_pool_address_y = self.base_pool_address
        else:
            self.coin_x = Tokens().get_by_contract_address(pool_data[0])
            self.coin_y = Tokens().get_by_contract_address(pool_data[1])

            self.fetch_local_tokens_data()
            if self.check_local_tokens_data() is False:
                logger.error(f"Error getting local tokens data")
                return None

            base_pool_address_x = pool_data[2]
            base_pool_address_y = pool_data[3]

        wallet_x_balance_decimals = self.initial_balance_x_wei / 10 ** self.token_x_decimals
        wallet_y_balance_decimals = self.initial_balance_y_wei / 10 ** self.token_y_decimals
        if self.initial_balance_x_wei == 0 or self.initial_balance_y_wei == 0:
            logger.error(
                f"Wallet token balance should be > 0,"
                f"({wallet_x_balance_decimals} {self.coin_x.symbol.upper()},"
                f"{wallet_y_balance_decimals} {self.coin_y.symbol.upper()})"
            )
            return

        if (wallet_x_balance_decimals < self.task.max_amount_out
                or wallet_y_balance_decimals < self.task.max_amount_out):

            lowest_token_balance = min(wallet_x_balance_decimals, wallet_y_balance_decimals)
            amount_out_decimals = random.uniform(self.task.min_amount_out, lowest_token_balance)
        else:
            amount_out_decimals = random.uniform(self.task.min_amount_out, self.task.max_amount_out)

        if self.task.use_all_balance is True:
            amount_out_x = self.initial_balance_x_wei
            amount_out_y = self.initial_balance_y_wei

        elif self.task.send_percent_balance:
            percent = random.randint(
                int(self.task.min_amount_out), int(self.task.max_amount_out)
            ) / 100
            amount_out_x = int(self.initial_balance_x_wei * percent)
            amount_out_y = int(self.initial_balance_y_wei * percent)

        else:
            amount_out_x = int(amount_out_decimals * 10 ** self.token_x_decimals)
            amount_out_y = int(amount_out_decimals * 10 ** self.token_y_decimals)

        return {
            self.coin_x.contract_address: amount_out_x,
            self.coin_y.contract_address: amount_out_y,
            "base_pool_address_x": base_pool_address_x,
            "base_pool_address_y": base_pool_address_y
        }

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        pair_data = self.get_amount_out_for_token_pair()
        if pair_data is None:
            logger.error(
                f"Error getting amount out for token pair: "
                f"{self.coin_x.symbol.upper()}/{self.coin_y.symbol.upper()}"
            )
            return

        try:
            amount_out_x = pair_data.get(self.coin_x.contract_address)
            amount_out_y = pair_data.get(self.coin_y.contract_address)
            if amount_out_x > self.initial_balance_x_wei:
                logger.error(
                    f"Amount out {amount_out_x / 10 ** self.token_x_decimals} "
                    f"is greater than wallet balance {self.initial_balance_x_wei / 10 ** self.token_x_decimals}"
                )
                return None

            if amount_out_y > self.initial_balance_y_wei:
                logger.error(
                    f"Amount out {amount_out_y / 10 ** self.token_y_decimals} "
                    f"is greater than wallet balance {self.initial_balance_y_wei / 10 ** self.token_y_decimals}"
                )
                return None

            base_pool_address_x = pair_data.get("base_pool_address_x")
            base_pool_address_y = pair_data.get("base_pool_address_y")

            transaction_args = [
                TransactionArgument(int(amount_out_x), Serializer.u64),
                TransactionArgument(int(amount_out_y), Serializer.u64),
                TransactionArgument(0, Serializer.u64),
                TransactionArgument(0, Serializer.u64),

            ]

            payload = EntryFunction.natural(
                f"{self.stable_scripts_address}",
                "add_liquidity",
                [
                    TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                    TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                    TypeTag(StructTag.from_str(base_pool_address_x)),
                    TypeTag(StructTag.from_str(base_pool_address_y))
                ],
                transaction_args
            )

            return TransactionPayloadData(
                payload=payload,
                amount_x_decimals=amount_out_x / 10 ** self.token_x_decimals,
                amount_y_decimals=amount_out_y / 10 ** self.token_y_decimals
            )

        except Exception as e:
            logger.error(f"Error while building transaction payload: {e}")
            return None

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_status = self.send_liquidity_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )

        ex_status = txn_status.execution_status

        if ex_status != enums.ModuleExecutionStatus.SUCCESS and ex_status != enums.ModuleExecutionStatus.SENT:
            return txn_status

        if self.task.reverse_action is True:
            delay = get_delay(self.task.min_delay_sec, self.task.max_delay_sec)
            logger.info(f"Waiting {delay} seconds before reverse action")
            time.sleep(delay)

            old_task = self.task.dict(exclude={"module_name",
                                               "module_type",
                                               "module"})

            task = self.task.reverse_action_task(**old_task)

            reverse_action = ThalaRemoveLiquidity(
                account=self.account,
                task=task,
                base_url=self.base_url,
            )
            reverse_txn_status = reverse_action.send_txn()
            return reverse_txn_status

        return txn_status


class ThalaRemoveLiquidity(ThalaLiquidityBase):

    def __init__(
            self,
            account: Account,
            task: 'ThalaRemoveLiquidityTask',
            base_url: str,
            proxies: dict = None
    ):
        super().__init__(
            account=account,
            task=task,
            base_url=base_url,
            proxies=proxies
        )

    def get_lp_ratio(
            self,
            coin_x_address: str,
            coin_y_address: str,
            base_pool_x: str,
            base_pool_y: str,
            account_address: AccountAddress
    ):

        lp_addr = f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePoolToken" \
                  f"<{coin_x_address}, {coin_y_address}, {base_pool_x}, {base_pool_y}>"

        token_info = self.client.account_resource(
            AccountAddress.from_hex("0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af"),
            f"0x1::coin::CoinInfo<{lp_addr}>"
        )
        lp_supply = token_info.get("data").get("supply").get("vec")[0].get("integer").get("vec")[0].get("value")

        wallet_lp_balance = self.get_wallet_lp_balance(account_address,
                                                       lp_addr)
        if wallet_lp_balance is None:
            return None

        lp_ratio = Math.fraction(int(wallet_lp_balance),
                                 int(lp_supply))

        return lp_ratio

    def get_amount_in_x_y(self, pool_data: list) -> Union[dict, None]:
        base_pool_address_x = pool_data[2]
        base_pool_address_y = pool_data[3]

        lp_ratio = self.get_lp_ratio(
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
            base_pool_x=base_pool_address_x,
            base_pool_y=base_pool_address_y,
            account_address=self.account.address()
        )
        if lp_ratio is None:
            return None

        liquidity_pool_data = self.get_liquidity_pool_data(
            coin_x_address=self.coin_x.contract_address,
            coin_y_address=self.coin_y.contract_address,
            base_pool_x=base_pool_address_x,
            base_pool_y=base_pool_address_y,
        )
        if liquidity_pool_data is None:
            logger.error(f"Error getting liquidity pool data")
            return

        lp_balance = liquidity_pool_data.get("data")
        if lp_balance is None:
            logger.error(f"Error getting lp balance")
            return

        lp_balance = lp_balance.get("balances")
        if lp_balance is None:
            logger.error(f"Error getting lp balance")
            return

        if len(lp_balance) < 2:
            logger.error(f"Error getting lp balance")
            return

        lp_balance_x = float(lp_balance[0]) * 10 ** 6
        lp_balance_y = float(lp_balance[1]) * 10 ** 6

        amount_in_x, amount_in_y = get_pair_amount_in(
            lp_balance_x=int(lp_balance_x),
            lp_balance_y=int(lp_balance_y),
            lp_ratio=lp_ratio
        )

        if amount_in_x is None or amount_in_y is None:
            logger.error(f"Error getting amount in")
            return

        return {
            self.coin_x.contract_address: amount_in_x,
            self.coin_y.contract_address: amount_in_y
        }

    def build_transaction_payload(self) -> Union[TransactionPayloadData, None]:
        pool_data = self.get_pool_for_token_pair()
        if pool_data is None:
            logger.error(f"Error getting pool data")
            return None

        self.coin_x = Tokens().get_by_contract_address(pool_data[0])
        self.coin_y = Tokens().get_by_contract_address(pool_data[1])
        self.fetch_local_tokens_data()

        if self.check_local_tokens_data() is False:
            logger.error(f"Error getting local tokens data")
            return None

        base_pool_address_x = pool_data[2]
        base_pool_address_y = pool_data[3]

        lp_addr = f"0x48271d39d0b05bd6efca2278f22277d6fcc375504f9839fd73f74ace240861af::stable_pool::StablePoolToken" \
                  f"<{self.coin_x.contract_address}, {self.coin_y.contract_address}, {base_pool_address_x}, {base_pool_address_y}>"

        wallet_lp_balance = self.get_wallet_lp_balance(
            account_address=self.account.address(),
            lp_address=lp_addr
        )
        if wallet_lp_balance is None:
            logger.error(f"Error getting wallet lp balance")
            return None

        if float(wallet_lp_balance) == 0:
            logger.error(f"Wallet lp balance is 0, nothing to remove")
            return None

        amount_in_x_y = self.get_amount_in_x_y(
            pool_data=pool_data
        )
        if amount_in_x_y is None:
            logger.error(f"Error getting amount in")
            return None

        amount_in_x = amount_in_x_y.get(self.coin_x.contract_address)
        amount_in_y = amount_in_x_y.get(self.coin_y.contract_address)
        if amount_in_x is None or amount_in_y is None:
            logger.error(f"Error getting amount in")
            return None

        transaction_args = [
            TransactionArgument(int(wallet_lp_balance), Serializer.u64),
            TransactionArgument(int(amount_in_x), Serializer.u64),
            TransactionArgument(int(amount_in_y), Serializer.u64),
            TransactionArgument(0, Serializer.u64),
            TransactionArgument(0, Serializer.u64)
        ]

        payload = EntryFunction.natural(
            f"{self.stable_scripts_address}",
            "remove_liquidity",
            [
                TypeTag(StructTag.from_str(self.coin_x.contract_address)),
                TypeTag(StructTag.from_str(self.coin_y.contract_address)),
                TypeTag(StructTag.from_str(base_pool_address_x)),
                TypeTag(StructTag.from_str(base_pool_address_y))
            ],
            transaction_args
        )

        return TransactionPayloadData(
            payload=payload,
            amount_x_decimals=amount_in_x / 10 ** self.token_x_decimals,
            amount_y_decimals=amount_in_y / 10 ** self.token_y_decimals
        )

    def send_txn(self) -> ModuleExecutionResult:
        if self.check_local_tokens_data() is False:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = f"Failed to fetch local tokens data"
            return self.module_execution_result

        txn_payload_data = self.build_transaction_payload()
        if txn_payload_data is None:
            self.module_execution_result.execution_status = enums.ModuleExecutionStatus.ERROR
            self.module_execution_result.execution_info = "Error while building transaction payload"
            return self.module_execution_result

        txn_status = self.send_liquidity_type_txn(
            account=self.account,
            txn_payload_data=txn_payload_data
        )
        return txn_status
