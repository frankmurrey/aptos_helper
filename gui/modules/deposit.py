from typing import Union, Callable
from tkinter import Variable
from tkinter import messagebox

import customtkinter
from loguru import logger
from pydantic.error_wrappers import ValidationError

from src import enums
from src.schemas import tasks
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame

DEPOSIT_TASKS = {
    enums.ModuleName.GATOR: tasks.GatorDepositTask
}


class DepositLendingTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.GatorDepositTask = None
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
        return DEPOSIT_TASKS.get(protocol)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            frame = self.withdraw_frame
            config_data: tasks.WithdrawTaskBase = config_schema(
                coin_x=frame.coin_x_combo.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                min_amount_out=frame.min_amount_entry.get(),
                max_amount_in=frame.max_amount_entry.get(),
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
            task: tasks.DepositTaskBase,
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

        # MIN AMOUNT
        self.min_amount_label = customtkinter.CTkLabel(self, text="Min amount:")
        self.min_amount_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")

        min_amount = getattr(self.task, "min_amount_out", "")
        self.min_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=min_amount))
        self.min_amount_entry.grid(row=5, column=0, padx=20, pady=0, sticky="w")

        # MAX AMOUNT
        self.max_amount_label = customtkinter.CTkLabel(self, text="Max amount:")
        self.max_amount_label.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="w")

        max_amount = getattr(self.task, "max_amount_out", "")
        self.max_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=max_amount))
        self.max_amount_entry.grid(row=5, column=1, padx=20, pady=0, sticky="w")

        # USE ALL BALANCE CHECKBOX
        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event,
        )
        self.use_all_balance_checkbox.grid(
            row=6, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        # SEND PERCENT BALANCE CHECKBOX
        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.send_percent_balance_checkbox.grid(
            row=7, column=0, padx=20, pady=(5, 20), sticky="w"
        )

        if getattr(self.task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        if getattr(self.task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

    @property
    def protocol_options(self) -> list:
        return [key.value.upper() for key in DEPOSIT_TASKS.keys()]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get()

        return [
            token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)
        ]

    def protocol_change_event(self, protocol=None):
        self.coin_x_combo.configure(values=self.protocol_coin_options)
        self.coin_x_combo.set(self.protocol_coin_options[0])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(state="disabled")
        else:
            self.min_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(state="normal")
