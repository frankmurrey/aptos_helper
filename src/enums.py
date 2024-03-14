from enum import Enum


class ModuleType(str, Enum):
    SWAP = "swap"
    MINT = "mint"
    SUPPLY = "supply"
    BORROW = "borrow"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    LIQUIDITY_ADD = "liq_add"
    LIQUIDITY_REMOVE = "liq_remove"
    SEND_MAIL = "send_mail"
    TEST = "test"
    SEND = "send"
    CLAIM = "claim"
    BRIDGE = "bridge"
    DELEGATE = "delegate"
    UNLOCK = "unlock"
    TRANSFER = "transfer"
    DRAW = "draw"
    COLLECT = "collect"
    PLACE_OPEN_ORDER = "open order"
    PLACE_CANCEL_ORDER = "cancel order"
    TRADE = "trade"
    UNSTAKE = "unstake"


class ModuleName(str, Enum):
    RANDOM = "random_task"
    THE_APTOS_BRIDGE = "aptos_bridge"
    PANCAKE = "pancake"
    LIQUID_SWAP = "liquid_swap"
    THALA = "thala"
    ABEL = "abel"
    TOKEN = "token"
    DELEGATE = "delegate"
    UNLOCK = "unlock"
    GRAFFIO = "graffio"
    NFT_COLLECT = "nft"
    MERKLE = "merkle"
    AMNIS = "amnis"
    GATOR = "gator"
    SUSHI = "sushi"


class TabName(str, Enum):
    SWAP = "Swap"
    ADD_LIQUIDITY = "Add Liquidity"
    REMOVE_LIQUIDITY = "Remove Liquidity"
    SUPPLY_LENDING = "Supply Lending"
    DEPOSIT = "Deposit"
    WITHDRAW = "Withdraw"
    TRANSFER = "Transfer"
    BRIDGE = "Aptos Bridge"
    DELEGATE = "Delegate"
    UNLOCK = "Unlock"
    NFT_COLLECT = "NFT Collect"
    MERKLE = "Merkle"
    TRADE = "Trade"
    MINT = "Mint"
    UNSTAKE = "Unstake"


class TaskStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class WalletStatus(str, Enum):
    active = "active"
    completed = "completed"
    inactive = "inactive"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"
    TIME_OUT = "time_out"


class ModuleExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    TEST_MODE = "test_mode"
    TIME_OUT = "time_out"
    SENT = "sent"
    ERROR = "error"


class MiscTypes(str, Enum):
    RANDOM = "random"


class RunMode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"


class OrderType(str, Enum):
    SHORT = "short"
    LONG = "long"
