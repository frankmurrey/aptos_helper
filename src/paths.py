import pathlib
import os

MAIN_DIR = os.path.join(pathlib.Path(__file__).parent.parent.resolve())

CONTRACTS_DIR = os.path.join(MAIN_DIR, "contracts")
CONFIG_DIR = os.path.join(MAIN_DIR, "config")
LOGS_DIR = os.path.join(MAIN_DIR, "logs")
GUI_DIR = os.path.join(MAIN_DIR, 'gui')
GUI_IMAGES_DIR = os.path.join(GUI_DIR, 'images')

APTOS_WALLETS_FILE = os.path.join(MAIN_DIR, "wallets.txt")
EVM_ADDRESSES_FILE = os.path.join(MAIN_DIR, "evm_addresses.txt")
PROXY_FILE = os.path.join(MAIN_DIR, "proxy.txt")

DARK_MODE_LOGO_IMG = os.path.join(GUI_IMAGES_DIR, 'dark_mode_logo.png')
LIGHT_MODE_LOGO_IMG = os.path.join(GUI_IMAGES_DIR, 'light_mode_logo.png')
TOOLS_LOGO = os.path.join(GUI_IMAGES_DIR, 'tools_logo.png')


class TempFiles:
    def __init__(self):
        self.TOKENS_JSON_FILE = os.path.join(CONTRACTS_DIR, "tokens.json")
        self.RPC_URLS_JSON_FILE = os.path.join(CONTRACTS_DIR, "rpc_urls.json")
        self.LOGS_DIR = LOGS_DIR


