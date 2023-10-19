from contracts.base import ChainBase

from loguru import logger


class Chains:
    def __init__(self):
        self.all_chains = [
            ChainBase(
                name="Optimism",
                chain_id=111,
                supported_tokens=["USDC"]
            ),

            ChainBase(
                name="Ethereum",
                chain_id=101,
                supported_tokens=["USDC", "USDT"]
            ),

            ChainBase(
                name="BSC",
                chain_id=102,
                supported_tokens=["USDC", "USDT"]
            ),

            ChainBase(
                name="Avalanche",
                chain_id=106,
                supported_tokens=["USDC", "USDT"]
            ),

            ChainBase(
                name="Polygon",
                chain_id=109,
                supported_tokens=["USDC", "USDT"]
            ),

            ChainBase(
                name="Arbitrum",
                chain_id=110,
                supported_tokens=["USDC", "USDT"]
            ),

        ]

    def get_by_name(self, name_query):
        for chain in self.all_chains:
            if chain.name.lower() == name_query.lower():
                return chain

        logger.error(f"Chain {name_query} not found")

        return None

