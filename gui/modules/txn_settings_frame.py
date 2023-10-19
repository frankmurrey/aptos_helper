import customtkinter
from tkinter import Variable


class TxnSettingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.frame = customtkinter.CTkFrame(master, width=100)
        self.frame.grid(**grid,)
        self.frame.grid_columnconfigure(0, weight=1)
        # self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.gas_price_label = customtkinter.CTkLabel(
            self.frame,
            text="Gas Price (Octa):"
        )
        self.gas_price_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(10, 0),
            sticky='w'
        )
        self.gas_price_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            state="normal",
            textvariable=Variable(value=100)
        )
        self.gas_price_entry.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w",
        )

        self.gas_limit_label = customtkinter.CTkLabel(
            self.frame,
            text="Gas Limit:"
        )
        self.gas_limit_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 0),
            sticky='w'
        )
        self.gas_limit_entry = customtkinter.CTkEntry(
            self.frame,
            width=100,
            state="normal",
            textvariable=Variable(value=10000)
        )
        self.gas_limit_entry.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w",
        )

        self.forced_gas_limit_check_box = customtkinter.CTkCheckBox(
            self.frame,
            text="Forced gas limit",
            checkbox_height=18,
            checkbox_width=18,
            onvalue=True,
            offvalue=False
        )
        self.forced_gas_limit_check_box.grid(
            row=4,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )
