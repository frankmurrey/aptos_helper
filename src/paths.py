import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())

CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")
CONFIG_DIR = os.path.join(MAIN_DIR, "config")

APTOS_WALLETS_FILE = os.path.join(MAIN_DIR, "wallets.txt")
EVM_ADDRESSES_FILE = os.path.join(MAIN_DIR, "evm_addresses.txt")
PROXY_FILE = os.path.join(MAIN_DIR, "proxy.txt")


class TempFiles:
    def __init__(self):
        self.TOKENS_JSON_FILE = os.path.join(CONTRACTS_DIR, "tokens.json")
        self.RPC_URLS_JSON_FILE = os.path.join(CONTRACTS_DIR, "rpc_urls.json")


