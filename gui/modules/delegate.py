from tkinter import Variable, messagebox

import customtkinter
from pydantic.error_wrappers import ValidationError

from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.right_frame.wallet_components.validator_address_entry import ValidatorAddressEntry


class DelegateTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.DelegateTask = None
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        delegate_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.delegate_frame = DelegateFrame(
            master=self.tabview.tab(tab_name),
            grid=delegate_frame_grid,
            task=task
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
        try:
            config_data = tasks.DelegateTask(
                validator_address=self.delegate_frame.validator_address_entry.get(),
                min_amount_out=self.delegate_frame.min_amount_entry.get(),
                max_amount_out=self.delegate_frame.max_amount_entry.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get()
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class DelegateFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.DelegateTask,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=0, uniform="a")
        self.grid_rowconfigure((0, 1), weight=1)

        # VALIDATOR ADDRESS
        address = getattr(self.task, "validator_address", None)
        self.validator_address_entry = ValidatorAddressEntry(
            self,
            pair_address=address,
        )
        self.validator_address_entry.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="w")

        # MIN AMOUNT
        self.min_amount_label = customtkinter.CTkLabel(self, text="Min amount:")
        self.min_amount_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")

        min_amount = getattr(self.task, "min_amount_out", "11")
        self.min_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=min_amount))
        self.min_amount_entry.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        # MAX AMOUNT
        self.max_amount_label = customtkinter.CTkLabel(self, text="Max amount:")
        self.max_amount_label.grid(row=1, column=0, padx=(270, 0), pady=(10, 0), sticky="w")

        max_amount = getattr(self.task, "max_amount_out", "11")
        self.max_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=max_amount))
        self.max_amount_entry.grid(row=2, column=0, padx=(270, 0), pady=(0, 20), sticky="w")
