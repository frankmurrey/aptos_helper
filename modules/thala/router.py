from typing import Dict, List, Tuple, Union, Optional
from enum import Enum

from loguru import logger

from src.schemas.misc import EntryFunctionPayloadData
from modules.thala.pool_data_client import PoolDataClient
from modules.thala.swap_math import calc_out_given_in_stable, calc_out_given_in_weighted
from modules.thala import abis
from modules.thala import types


DEFAULT_SWAP_FEE_STABLE = 0.001
DEFAULT_SWAP_FEE_WEIGHTED = 0.003

Predecessors = Dict[str, Dict[int, Optional[Tuple[str, types.LiquidityPool]]]]
Distances = Dict[str, Dict[int, float]]

ROUTER_ADDRESS = abis.STABLE_POOL_SCRIPTS_ABI["address"]
MULTI_HOP_ADDRESS = abis.MULTIHOP_ROUTER_ABI["address"]


class Edge:
    def __init__(self, from_index: int, to_index: int, pool: types.LiquidityPool):
        self.from_index = from_index
        self.to_index = to_index
        self.pool = pool


Graph = Dict[str, List[Edge]]


def parse_weights_from_weighted_pool_name(pool_name: str) -> List[float]:
    weights = []
    token_weight_pairs = pool_name.split(":")

    for pair in token_weight_pairs[1:]:
        parts = pair.split("-")
        if len(parts) == 2:
            try:
                weight = int(parts[1])
                weights.append(weight / 100)
            except ValueError:
                raise ValueError(f"Invalid weight in pool name: {pool_name}")
        else:
            raise ValueError(f"Invalid token-weight pair in pool name: {pool_name}")

    return weights


def parse_amp_factor_from_stable_pool_name(pool_name: str) -> int:
    parts = pool_name.split(":")
    try:
        return int(parts[1])
    except (IndexError, ValueError):
        raise ValueError(f"Invalid amp factor in pool name: {pool_name}")


class PoolType(Enum):
    STABLE_POOL = "stable_pool"
    WEIGHTED_POOL = "weighted_pool"


class LiquidityPool:
    def __init__(
            self,
            coin_addresses: List[str],
            balances: List[float],
            pool_type: PoolType,
            swap_fee: float,
            weights: Optional[List[float]] = None,
            amp: Optional[float] = None
    ):
        self.coin_addresses = coin_addresses
        self.balances = balances
        self.pool_type = pool_type
        self.swap_fee = swap_fee
        self.weights = weights
        self.amp = amp


def calc_out_given_in(
        amount_in: float,
        pool: LiquidityPool,
        from_index: int,
        to_index: int
) -> Union[float, None]:
    if pool.pool_type == PoolType.STABLE_POOL:

        return calc_out_given_in_stable(
            amount_in,
            from_index,
            to_index,
            pool.balances,
            pool.amp,
            pool.swap_fee
        )
    elif pool.pool_type == PoolType.WEIGHTED_POOL:
        weight_from = pool.weights[from_index]
        weight_to = pool.weights[to_index]

        return calc_out_given_in_weighted(
            pool.balances[from_index],
            weight_from,
            pool.balances[to_index],
            weight_to,
            amount_in,
            pool.swap_fee
        )
    else:
        return None


def build_graph(pools: List[types.Pool]) -> Graph:
    tokens = set()
    graph: Graph = {}

    for pool in pools:
        assets = [pool.asset0, pool.asset1, pool.asset2, pool.asset3]
        assets = [a for a in assets if a]

        balances = [pool.balance0, pool.balance1, pool.balance2, pool.balance3]
        balances = [balances[i] for i, a in enumerate(assets) if a]

        pool_type = PoolType.STABLE_POOL if pool.name[0] == "S" else PoolType.WEIGHTED_POOL
        swap_fee = DEFAULT_SWAP_FEE_STABLE if pool_type == PoolType.STABLE_POOL else DEFAULT_SWAP_FEE_WEIGHTED

        weights = parse_weights_from_weighted_pool_name(pool.name) if pool_type == PoolType.WEIGHTED_POOL else None
        amp = parse_amp_factor_from_stable_pool_name(pool.name) if pool_type == PoolType.STABLE_POOL else None

        converted_pool = types.LiquidityPool(
            coin_addresses=[a.address for a in assets],
            balances=balances,
            pool_type=pool_type,
            swap_fee=swap_fee,
            weights=weights,
            amp=amp
        )

        for i, asset in enumerate(assets):
            token = asset.address
            tokens.add(token)
            for j in range(len(assets)):
                if i != j:
                    if token not in graph:
                        graph[token] = []

                    graph[token].append(types.Edge(from_index=i, to_index=j, pool=converted_pool))

    return graph


def find_route_given_exact_input(
        graph: Dict[str, List['Edge']],
        start_token: str,
        end_token: str,
        amount_in: float,
        max_hops: int
) -> Union[types.Route, None]:
    tokens = list(graph.keys())
    distances: Distances = {token: {} for token in tokens}
    predecessors: Predecessors = {token: {} for token in tokens}

    default_distance = float('-inf')
    distances[start_token][0] = amount_in

    for i in range(max_hops):
        for edges in graph.values():
            for edge in edges:
                from_token = edge.pool.coin_addresses[edge.from_index]
                to_token = edge.pool.coin_addresses[edge.to_index]
                if from_token == end_token or to_token == start_token:
                    continue

                if i not in distances[from_token]:
                    continue

                new_distance = calc_out_given_in(
                    distances[from_token][i],
                    edge.pool,
                    edge.from_index,
                    edge.to_index
                )

                next_hop = i + 1
                if new_distance > distances.get(to_token, {}).get(next_hop, default_distance):
                    distances[to_token][next_hop] = new_distance
                    predecessors[to_token][next_hop] = (from_token, edge.pool)

    max_distance = float('-inf')
    hops = 0

    for i in range(1, max_hops + 1):
        distance = distances[end_token].get(i)
        if distance and distance > max_distance:
            max_distance = distance
            hops = i

    if max_distance == float('-inf'):
        logger.error("No route found")
        return None

    path = []
    current_token = end_token
    while hops > 0:
        token, pool = predecessors[current_token][hops]
        path.append({'from': token, 'to': current_token, 'pool': pool})
        current_token = token
        hops -= 1

    path.reverse()

    path = [types.SwapPath(
        from_coin=path[i]['from'],
        to=path[i]['to'],
        pool=path[i]['pool']
    ) for i in range(len(path))]

    return types.Route(
        path=path,
        amount_in=amount_in,
        amount_out=max_distance,
        price_impact_percentage=0,
        route_type="exact_input"
    )


stable_scripts_addr = abis.STABLE_POOL_SCRIPTS_ABI["address"]
NULL_TYPE = f"{stable_scripts_addr}::base_pool::Null"
NULL_4 = [NULL_TYPE for _ in range(4)]


def encode_weight(weight: float) -> str:
    addr = abis.WEIGHTED_POOL_SCRIPTS_ABI["address"]
    return f"{addr}::weighted_pool::Weight_{int(weight * 100)}"


def encode_pool_type(pool: LiquidityPool, extend_stable_args: bool) -> List[str]:
    if pool.pool_type == PoolType.STABLE_POOL:
        type_args = [pool.coin_addresses[i] if i < len(pool.coin_addresses) else NULL_TYPE for i in range(4)]
        return type_args + NULL_4 if extend_stable_args else type_args
    else:
        type_args_for_coins = [pool.coin_addresses[i] if i < len(pool.coin_addresses) else NULL_TYPE for i in range(4)]
        type_args_for_weights = [encode_weight(pool.weights[i]) if i < len(pool.weights) else NULL_TYPE for i in range(4)]
        return type_args_for_coins + type_args_for_weights


def calc_min_received_value(expected_amount_out: float, slippage: float) -> float:
    return expected_amount_out * (1 - slippage / 100)


def calc_max_sold_value(expected_amount_in: float, slippage: float) -> float:
    return expected_amount_in * (1 + slippage / 100)


def scale_up(amount: float, decimals: int) -> int:
    return int(amount * 10**decimals)


def encode_route(
        route: types.Route,
        slippage_percentage: float,
        token_in_decimals: Union[int, float],
        token_out_decimals: Union[int, float],
        balance_coin_in: Optional[float] = None,

) -> EntryFunctionPayloadData:
    if len(route.path) == 0 or len(route.path) > 3:
        raise ValueError("Invalid route")

    if route.route_type == "exact_input":
        if balance_coin_in is not None and balance_coin_in < route.amount_in:
            raise ValueError("Insufficient balance")

        amount_in_arg = scale_up(route.amount_in, token_in_decimals)
        amount_out_arg = scale_up(
            calc_min_received_value(route.amount_out, slippage_percentage),
            token_out_decimals
        )
    else:
        max_sold_value_after_slippage = calc_max_sold_value(route.amount_in, slippage_percentage)
        amount_in_arg = scale_up(min(balance_coin_in,
                                     max_sold_value_after_slippage) if balance_coin_in is not None else max_sold_value_after_slippage,
                                 token_in_decimals)
        amount_out_arg = scale_up(route.amount_out, token_out_decimals)

    if len(route.path) == 1:
        path = route.path[0]
        function_name = "swap_exact_in" if route.route_type == "exact_input" else "swap_exact_out"
        type_args = encode_pool_type(path.pool, False) + [path.from_coin, path.to]
        abi = abis.WEIGHTED_POOL_SCRIPTS_ABI if path.pool.pool_type == PoolType.WEIGHTED_POOL else abis.STABLE_POOL_SCRIPTS_ABI

        return EntryFunctionPayloadData(
            address=f"{abi['address']}::{abi['name']}",
            func_name=function_name,
            type_args=type_args,
            args=[amount_in_arg, amount_out_arg],
        )

    elif len(route.path) == 2:
        path0, path1 = route.path
        type_args = encode_pool_type(path0.pool, True) + encode_pool_type(path1.pool, True) + [path0.from_coin, path0.to, path1.to]
        function_name = "swap_exact_in_2" if route.route_type == "exact_input" else "swap_exact_out_2"
        abi = abis.MULTIHOP_ROUTER_ABI

        return EntryFunctionPayloadData(
            address=f"{abi['address']}::{abi['name']}",
            func_name=function_name,
            type_args=type_args,
            args=[amount_in_arg, amount_out_arg],
        )

    else:
        path0, path1, path2 = route.path
        type_args = encode_pool_type(path0.pool, True) + encode_pool_type(path1.pool, True) + encode_pool_type(
            path2.pool, True) + [path0.from_coin, path0.to, path1.to, path2.to]
        function_name = "swap_exact_in_3" if route.route_type == "exact_input" else "swap_exact_out_3"
        abi = abis.MULTIHOP_ROUTER_ABI

        return EntryFunctionPayloadData(
            address=f"{abi['address']}::{abi['name']}",
            func_name=function_name,
            type_args=type_args,
            args=[amount_in_arg, amount_out_arg],
        )


def test():
    pdcli = PoolDataClient(data_url="https://app.thala.fi/api/pool-balances")
    pool_data = pdcli.get_pool_data()

    graph = build_graph(pool_data.pools)

    route = find_route_given_exact_input(
        graph=graph,
        start_token="0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDC",
        end_token="0x6f986d146e4a90b828d8c12c14b6f4e003fdff11a8eecceceb63744363eaac01::mod_coin::MOD",
        amount_in=10,
        max_hops=5
    )

    encoded_route = encode_route(
        route=route,
        slippage_percentage=0.5,
        token_in_decimals=6,
        token_out_decimals=6
    )
    print(encoded_route)



if __name__ == '__main__':
    test()
