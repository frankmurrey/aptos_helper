import customtkinter
from tkinter import Variable
from src.schemas import tasks


class TxnSettingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.TaskBase = None,
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master, width=100)
        self.frame.grid(**grid,)
        self.frame.grid_columnconfigure(0, weight=1)

        self.gas_limit_label = customtkinter.CTkLabel(
            self.frame,
            text="Gas Limit:"
        )
        self.gas_limit_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )

        gas_limit = getattr(task, "gas_limit", "") if getattr(task, "forced_gas_limit", False) else 10000
        self.gas_limit_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            textvariable=Variable(value=gas_limit)
        )
        self.gas_limit_entry.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w",
        )

        check_box_value = getattr(task, "forced_gas_limit", False)
        self.forced_gas_limit_check_box = customtkinter.CTkCheckBox(
            self.frame,
            text="Forced gas limit",
            checkbox_height=18,
            checkbox_width=18,
            onvalue=True,
            offvalue=False
        )
        self.forced_gas_limit_check_box.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )
        if check_box_value:
            self.forced_gas_limit_check_box.select()

        self.gas_price_label = customtkinter.CTkLabel(
            self.frame,
            text="Gas Price (Octa):"
        )
        self.gas_price_label.grid(
            row=0,
            column=0,
            padx=(160, 20),
            pady=(10, 0),
            sticky='w'
        )

        gas_price = getattr(task, "gas_price", "") if getattr(task, "forced_gas_limit", False) else 100
        self.gas_price_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            textvariable=Variable(value=gas_price)
        )
        self.gas_price_entry.grid(
            row=1,
            column=0,
            padx=(160, 20),
            pady=(0, 10),
            sticky="w",
        )
