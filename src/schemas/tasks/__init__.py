from .base import TaskBase
from .base.add_liquidity import AddLiquidityTaskBase
from .base.remove_liquidity import RemoveLiquidityTaskBase
from .base.supply import SupplyTaskBase
from .base.swap import SwapTaskBase
from .base.trade import TradeTaskBase
from .base.withdraw import WithdrawTaskBase
from .base.deposit import DepositTaskBase


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
from .merkle import MerklePlaceOpenOrderTask
from .merkle import MerklePlaceCancelOrderTask
from .amnis import AmnisMintAndStakeTask
from .amnis import AmnisUnstakeTask
from .gator import GatorTradeTask
from .gator import GatorDepositTask
from .gator import GatorWithdrawTask
from .sushi import SushiSwapTask

from .random_task.swap import RandomSwapTask
from .random_task.liquidity import RandomAddLiquidityTask

from .virtual_task.pancake import PancakeSwapVirtualTask
from .virtual_task.liquid_swap import LiquidSwapSwapVirtualTask
from .virtual_task.liquid_swap import LiquidSwapAddLiquidityVirtualTask
from .virtual_task.liquid_swap import LiquidSwapRemoveLiquidityVirtualTask
from .virtual_task.thala import ThalaAddLiquidityVirtualTask
from .virtual_task.thala import ThalaRemoveLiquidityVirtualTask
from .virtual_task.thala import ThalaSwapVirtualTask
from .virtual_task.thala import ThalaWithdrawVirtualTask
from .virtual_task.abel import AbelSupplyVirtualTask
from .virtual_task.abel import AbelWithdrawVirtualTask
from .virtual_task.merkle import MerklePlaceOpenOrderVirtualTask
from .virtual_task.merkle import MerklePlaceCancelOrderVirtualTask
from .virtual_task.amnis import AmnisMintAndStakeVirtualTask
from .virtual_task.amnis import AmnisUnstakeVirtualTask
from .virtual_task.gator import GatorTradeVirtualTask
from .virtual_task.gator import GatorDepositVirtualTask
from .virtual_task.gator import GatorWithdrawVirtualTask
from .virtual_task.sushi import SushiSwapVirtualTask
