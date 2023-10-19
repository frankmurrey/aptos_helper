from typing import Callable
from typing import Union
from tkinter import messagebox

import customtkinter

from tkinter import Variable
from loguru import logger
from pydantic.error_wrappers import ValidationError

from src import enums
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import ComboWithRandomCheckBox
from src.schemas.tasks.base.add_liquidity import AddLiquidityTaskBase
from src.schemas import tasks


class AddLiquidityTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        liquidity_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.liquidity_frame = AddLiquidityFrame(
            master=self.tabview.tab(tab_name),
            grid=liquidity_frame_grid
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
        protocol = self.liquidity_frame.protocol_combo.get_value().lower()
        if self.liquidity_frame.protocol_combo.get_checkbox_value():
            return tasks.RandomAddLiquidityTask

        else:
            if protocol == enums.ModuleName.LIQUID_SWAP:
                return tasks.LiquidSwapAddLiquidityTask

            elif protocol == enums.ModuleName.THALA:
                return tasks.ThalaAddLiquidityTask

            else:
                return None

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: AddLiquidityTaskBase = config_schema(
                coin_x=self.liquidity_frame.coin_x_combobox.get(),
                coin_y=self.liquidity_frame.coin_y_combobox.get_value(),
                random_y_coin=self.liquidity_frame.coin_y_combobox.get_checkbox_value(),
                use_all_balance=self.liquidity_frame.use_all_balance_x_checkbox.get(),
                send_percent_balance=self.liquidity_frame.send_percent_balance_x_checkbox.get(),
                min_amount_out=self.liquidity_frame.min_amount_out_x_entry.get(),
                max_amount_out=self.liquidity_frame.max_amount_out_x_entry.get(),
                slippage=self.liquidity_frame.slippage_entry.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                reverse_action=self.liquidity_frame.reverse_action_checkbox.get(),
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error",
                message=error_messages
            )
            return None


class AddLiquidityFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight=1)

        self.protocol_label = customtkinter.CTkLabel(
            self,
            text="Protocol:"
        )

        self.protocol_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        self.protocol_combo = ComboWithRandomCheckBox(
            self,
            grid={
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 0,
                "sticky": "w"
            },
            options=self.protocol_options,
            combo_command=self.protocol_change_event,
            text="Random protocol",
        )

        self.coin_x_label = customtkinter.CTkLabel(
            self,
            text="Coin X:"
        )
        self.coin_x_label.grid(
            row=3,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.coin_x_combobox = customtkinter.CTkComboBox(
            self,
            values=self.coin_x_options,
            width=120,
            command=self.update_coin_options
        )
        self.coin_x_combobox.grid(
            row=4,
            column=0,
            padx=20,
            pady=(0, 0),
            sticky="w"
        )

        self.coin_y_label = customtkinter.CTkLabel(
            self,
            text="Coin Y:"
        )
        self.coin_y_label.grid(
            row=3,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.coin_y_combobox = ComboWithRandomCheckBox(
            self,
            grid={"row": 4, "column": 1, "padx": 20, "pady": 0, "sticky": "w"},
            options=self.coin_y_options,
            text="Random Y coin",
        )

        self.reverse_action_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Make reverse action",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.reverse_action_checkbox.grid(
            row=5, column=0, padx=20, pady=(5, 0), sticky="w"
        )

        self.min_amount_out_x_label = customtkinter.CTkLabel(
            self,
            text="Min Amount Out X:"
        )
        self.min_amount_out_x_label.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.min_amount_out_x_entry = customtkinter.CTkEntry(
            self,
            width=130
        )
        self.min_amount_out_x_entry.grid(
            row=7,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="w"
        )

        self.max_amount_out_x_label = customtkinter.CTkLabel(
            self,
            text="Max Amount Out X:"
        )
        self.max_amount_out_x_label.grid(
            row=6,
            column=1,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.max_amount_out_x_entry = customtkinter.CTkEntry(
            self,
            width=130
        )
        self.max_amount_out_x_entry.grid(
            row=7,
            column=1,
            padx=20,
            pady=(0, 20),
            sticky="w"
        )

        self.use_all_balance_x_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use All Balance X",
            checkbox_width=18,
            checkbox_height=18,
            onvalue=True,
            offvalue=False,
            command=self.use_all_balance_checkbox_event
        )
        self.use_all_balance_x_checkbox.grid(
            row=8,
            column=0,
            padx=20,
            pady=(0, 0),
            sticky="w"
        )

        self.send_percent_balance_x_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send Percent Balance X",
            checkbox_width=18,
            checkbox_height=18,
            onvalue=True,
            offvalue=False

        )

        self.send_percent_balance_x_checkbox.grid(
            row=9,
            column=0,
            padx=20,
            pady=(5, 10),
            sticky="w"
        )

        self.slippage_label = customtkinter.CTkLabel(
            self,
            text="Slippage (%):",
        )
        self.slippage_label.grid(
            row=10,
            column=0,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.slippage_entry = customtkinter.CTkEntry(
            self,
            width=70,
            textvariable=Variable(value=0.5)
        )
        self.slippage_entry.grid(
            row=11,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="w"
        )

    @property
    def protocol_options(self) -> list:
        return [
            enums.ModuleName.LIQUID_SWAP.upper(),
            enums.ModuleName.THALA.upper(),
        ]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combo.get_value()
        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    @property
    def coin_x_options(self) -> list:
        return self.protocol_coin_options

    @property
    def coin_y_options(self) -> list:
        protocol_coin_options = self.protocol_coin_options
        coin_x = self.coin_x_combobox.get().lower()

        return [coin.upper() for coin in protocol_coin_options if coin.lower() != coin_x.lower()]

    def update_coin_options(self, event=None):
        coin_x_options = self.coin_x_options
        self.coin_x_combobox.configure(values=coin_x_options)

        coin_to_receive_options = self.coin_y_options
        self.coin_y_combobox.combobox.configure(values=coin_to_receive_options)
        self.coin_y_combobox.combobox.set(coin_to_receive_options[1])

    def protocol_change_event(self, protocol=None):
        coin_x_options = self.coin_x_options
        self.coin_x_combobox.configure(values=coin_x_options)
        self.coin_x_combobox.set(coin_x_options[1])

        coin_to_receive_options = self.coin_y_options
        self.coin_y_combobox.combobox.configure(values=coin_to_receive_options)
        self.coin_y_combobox.combobox.set(coin_to_receive_options[1])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_x_checkbox.get():
            self.min_amount_out_x_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_out_x_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_x_checkbox.deselect()
            self.send_percent_balance_x_checkbox.configure(
                state="disabled"
            )
        else:
            self.min_amount_out_x_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.max_amount_out_x_entry.configure(
                state="normal",
                fg_color='#343638',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_x_checkbox.configure(
                state="normal"
            )
