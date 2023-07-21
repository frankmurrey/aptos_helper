from contracts.base import Chain
from contracts.tokens import Tokens

from loguru import logger


class Chains:
    def __init__(self):
        self.all_chains = [
            Chain(name="Optimism",
                  chain_id=111,
                  supported_tokens=["USDC"]),

            Chain(name="Ethereum",
                  chain_id=101,
                  supported_tokens=["USDC", "USDT"]),

            Chain(name="BSC",
                  chain_id=102,
                  supported_tokens=["USDC", "USDT"]),

            Chain(name="Avalanche",
                  chain_id=106,
                  supported_tokens=["USDC", "USDT"]),

            Chain(name="Polygon",
                  chain_id=109,
                  supported_tokens=["USDC", "USDT"]),

            Chain(name="Arbitrum",
                  chain_id=110,
                  supported_tokens=["USDC", "USDT"]),

        ]

    def get_by_name(self, name_query):
        for chain in self.all_chains:
            if chain.name.lower() == name_query.lower():
                return chain
        logger.error(f"Chain {name_query} not found")
        return None

