from typing import Union, Callable

import customtkinter
from loguru import logger
from pydantic.error_wrappers import ValidationError
from tkinter import messagebox

from src import enums
from src.schemas import tasks
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame

WITHDRAW_TASKS = {
    enums.ModuleName.ABEL: tasks.AbelWithdrawTask,
    enums.ModuleName.THALA: tasks.ThalaWithdrawTask,
}


class WithdrawLendingTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.WithdrawTaskBase = None
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        withdraw_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.withdraw_frame = WithdrawLendingFrame(
            master=self.tabview.tab(tab_name),
            grid=withdraw_frame_grid,
            task=task
        )

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            }
        )

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.withdraw_frame.protocol_combo.get().lower()
        return WITHDRAW_TASKS.get(protocol)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: tasks.WithdrawTaskBase = config_schema(
                coin_x=self.withdraw_frame.coin_x_combo.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
            )
            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class WithdrawLendingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.WithdrawTaskBase,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # PROTOCOL
        self.protocol_label = customtkinter.CTkLabel(
            master=self,
            text="Protocol"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.protocol_combo = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_options,
            width=120,
            command=self.protocol_change_event
        )
        protocol = getattr(self.task, "module_name", self.protocol_options[0])
        self.protocol_combo.set(value=protocol.upper())
        self.protocol_combo.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # COIN_X
        self.coin_x = customtkinter.CTkLabel(
            master=self,
            text="Token to Supply"
        )
        self.coin_x.grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        coin_x = getattr(self.task, "coin_x", self.protocol_coin_options[0])
        self.coin_x_combo = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_coin_options,
            width=120,
        )
        self.coin_x_combo.set(value=coin_x.upper())
        self.coin_x_combo.grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 20)
        )

    @property
    def protocol_options(self) -> list:
        return [key.value.upper() for key in WITHDRAW_TASKS.keys()]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get()
        if 'thala' in protocol.lower():
            return ['MOD']

        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    def protocol_change_event(self, protocol=None):
        if protocol == enums.ModuleName.THE_APTOS_BRIDGE.upper():
            self.coin_x_combo.configure(state="disabled")
            self.coin_x_combo.configure(fg_color="#3f3f3f")

        else:
            self.coin_x_combo.configure(state="normal")
            self.coin_x_combo.configure(fg_color="#343638")
            coin_to_supply_options = self.protocol_coin_options
            self.coin_x_combo.configure(values=coin_to_supply_options)
            self.coin_x_combo.set(coin_to_supply_options[0])