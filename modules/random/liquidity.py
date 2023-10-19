import random
from modules.base import LiquidityModuleBase
from contracts.tokens.main import Tokens
from src.schemas.action_models import ModuleExecutionResult
from src.schemas.tasks import AddLiquidityTaskBase
from src.schemas import tasks


LIQUIDITY_TASKS = [
    tasks.LiquidSwapAddLiquidityTask,
    tasks.ThalaAddLiquidityTask,
]


class RandomAddLiquidity(LiquidityModuleBase):
    def __init__(
            self,
            account,
            base_url: str,
            task: AddLiquidityTaskBase,
            proxies: dict = None,
    ):
        super().__init__(
            account=account,
            base_url=base_url,
            task=task,
            proxies=proxies,
        )

        random_task_class = random.choice(LIQUIDITY_TASKS)
        task_dict = self.task.dict(exclude={"module_name",
                                            "module_type",
                                            "module"})
        random_task: AddLiquidityTaskBase = random_task_class(**task_dict)
        if random_task.random_y_coin:
            protocol_coins_obj = Tokens().get_tokens_by_protocol(random_task.module_name)
            protocol_coins = [coin.symbol for coin in protocol_coins_obj]
            protocol_coins.remove(random_task.coin_x.lower())
            random_task.coin_y = random.choice(protocol_coins)

            self.task = random_task

            self.coin_x = self.tokens.get_by_name(self.task.coin_x)
            self.coin_y = self.tokens.get_by_name(self.task.coin_y)

            self.initial_balance_x_wei = self.get_wallet_token_balance(
                wallet_address=self.account.address(),
                token_address=self.coin_x.contract_address
            )
            self.initial_balance_y_wei = self.get_wallet_token_balance(
                wallet_address=self.account.address(),
                token_address=self.coin_y.contract_address
            )
            self.token_x_decimals = self.get_token_decimals(token_obj=self.coin_x)
            self.token_y_decimals = self.get_token_decimals(token_obj=self.coin_y)

    def try_send_txn(
            self,
            retries: int = 1,
    ) -> ModuleExecutionResult:
        """
        Try to send transaction
        :param retries:
        :return:
        """

        module = self.task .module(
            account=self.account,
            task=self.task ,
            base_url=self.base_url,
            proxies=self.proxies,
        )
        return module.try_send_txn(retries=retries)
