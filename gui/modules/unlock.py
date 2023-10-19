import customtkinter
from src.schemas import tasks

from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.wallet_right_window.wallet_window.validator_address_entry import ValidatorAddressEntry


class UnlockTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        unlock_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.unlock_frame = UnlockFrame(
            master=self.tabview.tab(tab_name),
            grid=unlock_frame_grid
        )

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": (0, 20),
            "sticky": "nsew",
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_grid
        )

    def build_config_data(self):
        return tasks.UnlockTask(
            gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
            gas_price=self.txn_settings_frame.gas_price_entry.get(),
            forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            validator_address=self.unlock_frame.validator_address_entry.get(),
        )


class UnlockFrame(customtkinter.CTkFrame):
    def __init__(self, master, grid, **kwargs):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)
        self.frame.grid_columnconfigure((0, 1), weight=0, uniform="a")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

        self.validator_address_entry = ValidatorAddressEntry(
            self.frame,
            pair_address="",
        )
        self.validator_address_entry.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="w")





