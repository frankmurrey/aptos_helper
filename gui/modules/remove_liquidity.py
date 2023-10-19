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
from src.schemas.tasks.base.remove_liquidity import RemoveLiquidityTaskBase
from src.schemas import tasks


class RemoveLiquidityTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        liquidity_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.liquidity_frame = RemoveLiquidityFrame(
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
        swap_protocol = self.liquidity_frame.protocol_combo.get().lower()
        if swap_protocol == enums.ModuleName.LIQUID_SWAP:
            return tasks.LiquidSwapRemoveLiquidityTask

        elif swap_protocol == enums.ModuleName.THALA:
            return tasks.ThalaRemoveLiquidityTask

        else:
            return None

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data: RemoveLiquidityTaskBase = config_schema(
                coin_x=self.liquidity_frame.coin_x_combobox.get(),
                coin_y=self.liquidity_frame.coin_y_combobox.get(),
                slippage=self.liquidity_frame.slippage_entry.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get()
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error",
                message=error_messages
            )
            return None


class RemoveLiquidityFrame(customtkinter.CTkFrame):
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

        self.protocol_combo = customtkinter.CTkComboBox(
            self,
            values=self.protocol_options,
            width=130,
            command=self.protocol_change_event
        )
        self.protocol_combo.grid(
            row=1,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.coin_x_label = customtkinter.CTkLabel(
            self,
            text="Coin X:"
        )
        self.coin_x_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky="w"
        )

        self.coin_x_combobox = customtkinter.CTkComboBox(
            self,
            values=self.coin_x_options,
            width=130,
            command=self.update_coin_options
        )
        self.coin_x_combobox.grid(
            row=3,
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
            row=2,
            column=1,
            padx=(20, 20),
            pady=(10, 0),
            sticky="w"
        )

        self.coin_y_combobox = customtkinter.CTkComboBox(
            self,
            values=self.coin_y_options,
            width=130
        )
        self.coin_y_combobox.grid(
            row=3,
            column=1,
            padx=20,
            pady=(0, 0),
            sticky="w"
        )

        self.slippage_label = customtkinter.CTkLabel(
            self,
            text="Slippage (%):",
        )
        self.slippage_label.grid(
            row=4,
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
            row=5,
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
        protocol = self.protocol_combo.get()
        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    @property
    def coin_x_options(self) -> list:
        return self.protocol_coin_options

    @property
    def coin_y_options(self) -> list:
        protocol_coin_options = self.protocol_coin_options
        coin_to_swap = self.coin_x_combobox.get().lower()

        return [coin.upper() for coin in protocol_coin_options if coin.lower() != coin_to_swap.lower()]

    def update_coin_options(self, event=None):
        coin_to_swap_options = self.coin_x_options
        self.coin_x_combobox.configure(values=coin_to_swap_options)

        coin_to_receive_options = self.coin_y_options
        self.coin_y_combobox.configure(values=coin_to_receive_options)
        self.coin_y_combobox.set(coin_to_receive_options[1])

    def protocol_change_event(self, protocol=None):
        coin_to_swap_options = self.coin_x_options
        self.coin_x_combobox.configure(values=coin_to_swap_options)
        self.coin_x_combobox.set(coin_to_swap_options[1])

        coin_to_receive_options = self.coin_y_options
        self.coin_y_combobox.configure(values=coin_to_receive_options)
        self.coin_y_combobox.set(coin_to_receive_options[1])