from .base import TaskBase
from .base.add_liquidity import AddLiquidityTaskBase
from .base.remove_liquidity import RemoveLiquidityTaskBase
from .base.supply import SupplyTaskBase
from .base.swap import SwapTaskBase
from .base.withdraw import WithdrawTaskBase


from .the_aptos_bridge import TheAptosBridgeTask
from .the_aptos_bridge import TheAptosBridgeClaimTask
from .pancake import PancakeSwapTask
from .liquid_swap import LiquidSwapSwapTask
from .liquid_swap import LiquidSwapAddLiquidityTask
from .liquid_swap import LiquidSwapRemoveLiquidityTask
from .thala import ThalaAddLiquidityTask
from .thala import ThalaRemoveLiquidityTask
from .thala import ThalaSwapTask
from .thala import ThalaSupplyTask
from .thala import ThalaWithdrawTask
from .abel import AbelSupplyTask
from .abel import AbelWithdrawTask
from .delegate import DelegateTask
from .delegate import UnlockTask
from .transfer import TransferTask
from .graffio import GraffioDrawTask
from .nft_collect import NftCollectTask
from .nft_collect import NftCollectTask
from .merkle import MerklePlaceOrderTask

from .random_task.swap import RandomSwapTask
from .random_task.liquidity import RandomAddLiquidityTask
