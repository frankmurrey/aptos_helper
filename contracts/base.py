class TokenBase:
    def __init__(
            self,
            symbol: str,
            contract_address: str,
            aptos_bridge_handle: str = None,
            gecko_id: str = None,
            available_protocols: list = None,
    ):
        if available_protocols is None:
            available_protocols = []

        self.address, self.prefix, self.name = contract_address.split("::")
        self.symbol = symbol
        self.available_protocols = available_protocols
        self.aptos_bridge_handle = aptos_bridge_handle
        self.contract_address = contract_address

        self.coin_gecko_id = gecko_id


class ChainBase:
    def __init__(
            self,
            name: str,
            chain_id: int,
            supported_tokens: list
    ):
        self.name = name
        self.id = chain_id
        self.supported_tokens = supported_tokens
