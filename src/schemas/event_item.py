from src.schemas.tasks import TaskBase
from src.schemas.wallet_data import WalletData


class EventItem:
    """
    Base class for event items.
    """
    def get_data(self):
        return tuple(self.__dict__.values())

    def __repr__(self):
        return self.__str__()


class WalletEventItem(EventItem):
    """
    Base class for wallet event items.
    """
    def __init__(self, wallet: WalletData):
        self.wallet = wallet

    def __str__(self):
        return f"<WalletEventItem Wallet: {self.wallet.wallet_id}>"


class TaskEventItem(EventItem):
    """
    Base class for task event items.
    """
    def __init__(self, task: TaskBase, wallet: WalletData):
        self.task = task
        self.wallet = wallet

    def __str__(self):
        return f"<TaskEventItem Task: {self.task.task_id} Wallet: {self.wallet.wallet_id}>"


class WalletStartedEventItem(WalletEventItem):
    """
    Wallet started event item.
    """
    pass


class TaskStartedEventItem(TaskEventItem):
    """
    Task started event item.
    """
    pass


class WalletCompletedEventItem(WalletEventItem):
    """
    Wallet completed event item.
    """
    pass


class TaskCompletedEventItem(TaskEventItem):
    """
    Task completed event item.
    """
    pass
