from enum import Enum


class ModuleType(str, Enum):
    SWAP = "swap"
    MINT = "mint"
    SUPPLY = "supply"
    BORROW = "borrow"
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
