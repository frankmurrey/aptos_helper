from typing import Union, Callable
from tkinter import messagebox
from tkinter import Variable

import customtkinter
from loguru import logger
from pydantic.error_wrappers import ValidationError

from src import enums
from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame

MINT_TASKS = {
    enums.ModuleName.AMNIS: tasks.AmnisMintAndStakeTask
}


class MintTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task=None
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        mint_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.mint_frame = MintFrame(
            master=self.tabview.tab(tab_name),
            grid=mint_frame_grid,
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
        self.txn_settings_frame.gas_limit_entry.configure(textvariable=Variable(value=20000))

    def get_config_schema(self) -> Union[Callable, None]:
        protocol = self.mint_frame.protocol_combo.get().lower()
        return MINT_TASKS.get(protocol)

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            config_data = config_schema(
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


class MintFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task,
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
            width=120
        )
        protocol = getattr(self.task, "module_name", self.protocol_options[0])
        self.protocol_combo.set(value=protocol.upper())
        self.protocol_combo.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 20)
        )

    @property
    def protocol_options(self) -> list:
        return [key.value.upper() for key in MINT_TASKS.keys()]
