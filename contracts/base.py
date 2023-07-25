

class Token:
    def __init__(self,
                 symbol: str,
                 contract: str,
                 is_pancake_available: bool = False,
                 aptos_bridge_handle: str = None,
                 is_abel_available: bool = False,
                 is_thala_available: bool = False,
                 is_liquid_swap_available: bool = False):

        self.contract = contract
        self.address, self.prefix, self.name = contract.split("::")
        self.symbol = symbol
        self.is_pancake_available = is_pancake_available
        self.aptos_bridge_handle = aptos_bridge_handle
        self.is_abel_available = is_abel_available
        self.is_thala_available = is_thala_available
        self.is_liquid_swap_available = is_liquid_swap_available


class Chain:
    def __init__(self,
                 name: str,
                 chain_id: int,
                 supported_tokens: list):
        self.name = name
        self.id = chain_id
        self.supported_tokens = supported_tokens
