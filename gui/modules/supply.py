from typing import Callable, Union

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable, messagebox
from loguru import logger

from src import enums
from src.schemas import tasks
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame

SUPPLY_TASKS = {
    enums.ModuleName.ABEL: tasks.AbelSupplyTask,
    enums.ModuleName.THALA: tasks.ThalaSupplyTask,
}


class SupplyLendingTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.SupplyTaskBase
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        supply_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.supply_frame = SupplyLending(
            master=self.tabview.tab(tab_name),
            grid=supply_frame_grid,
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
        protocol = self.supply_frame.protocol_combo.get().lower()
        return SUPPLY_TASKS.get(protocol)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: tasks.SupplyTaskBase = config_schema(
                coin_x=self.supply_frame.coin_x_combo.get(),
                min_amount_out=self.supply_frame.min_amount_out_entry.get(),
                max_amount_out=self.supply_frame.max_amount_out_entry.get(),
                use_all_balance=self.supply_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.supply_frame.send_percent_balance_checkbox.get(),
                enable_collateral=self.supply_frame.enable_collateral_checkbox.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                reverse_action=self.supply_frame.reverse_action_checkbox.get(),
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class SupplyLending(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.SupplyTaskBase,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

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

        # TOKEN TO SUPPLY
        self.coin_x = customtkinter.CTkLabel(
            master=self,
            text="Coin to Supply"
        )
        self.coin_x.grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.coin_x_combo = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_coin_options,
            width=120
        )
        coin_x = getattr(self.task, "coin_x", self.protocol_coin_options[0])
        self.coin_x_combo.set(value=coin_x.upper())
        self.coin_x_combo.grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # REVERSE ACTION
        self.reverse_action_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Make reverse action",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        if getattr(self.task, "reverse_action", False):
            self.reverse_action_checkbox.select()

        self.reverse_action_checkbox.grid(
            row=4, column=0, padx=20, pady=(5, 0), sticky="w"
        )

        # MIN AMOUNT OUT
        self.min_amount = customtkinter.CTkLabel(
            master=self,
            text="Min amount out:"
        )
        self.min_amount.grid(
            row=5,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        min_amount = getattr(self.task, "min_amount_out", "")
        self.min_amount_out_entry = customtkinter.CTkEntry(
            master=self,
            width=120,
            textvariable=Variable(value=min_amount)
        )
        self.min_amount_out_entry.grid(
            row=6,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # MAX AMOUNT OUT
        self.max_amount = customtkinter.CTkLabel(
            master=self,
            text="Max amount out:"
        )
        self.max_amount.grid(
            row=5,
            column=1,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        max_amount = getattr(self.task, "max_amount_out", "")
        self.max_amount_out_entry = customtkinter.CTkEntry(
            master=self,
            width=120,
            textvariable=Variable(value=max_amount)
        )
        self.max_amount_out_entry.grid(
            row=6,
            column=1,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # USE ALL BALANCE
        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Use All Balance",
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event
        )
        self.use_all_balance_checkbox.grid(
            row=7,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Send Percent Balance",
            checkbox_width=18,
            checkbox_height=18
        )
        self.send_percent_balance_checkbox.grid(
            row=8,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )
        if getattr(self.task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        if getattr(self.task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

        self.enable_collateral_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Enable Collateral",
            checkbox_width=18,
            checkbox_height=18
        )
        self.enable_collateral_checkbox.grid(
            row=9,
            column=0,
            sticky="w",
            padx=20,
            pady=10
        )

    @property
    def protocol_options(self) -> list:
        return [key.value.upper() for key in SUPPLY_TASKS.keys()]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get()
        if 'thala' in protocol.lower():
            return ['MOD']

        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    def update_coin_options(self, event=None):
        coin_to_supply_options = self.protocol_coin_options
        self.coin_x_combo.configure(values=coin_to_supply_options)

    def protocol_change_event(self, protocol=None):
        coin_to_supply_options = self.protocol_coin_options
        self.coin_x_combo.configure(values=coin_to_supply_options)
        self.coin_x_combo.set(coin_to_supply_options[0])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )
        else:
            self.min_amount_out_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.max_amount_out_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(
                state="normal"
            )
