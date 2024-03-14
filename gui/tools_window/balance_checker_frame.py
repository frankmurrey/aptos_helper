from tkinter import filedialog
from tkinter import messagebox

import customtkinter

from gui.objects import FloatSpinbox
from gui.right_frame.main_frame import RightFrame
from src.storage import Storage
from contracts.tokens.main import Tokens
from utils.balance_checker import BalanceChecker
from utils.xlsx import write_balance_data_to_xlsx


class BalanceCheckerFrame(customtkinter.CTkFrame):
    def __init__(self, master, right_frame, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)

        self.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.right_frame: RightFrame = right_frame

        self.label = customtkinter.CTkLabel(
            master=self,
            text="Get wallets balances:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=15)

        self.token_label = customtkinter.CTkLabel(
            master=self,
            text="Token:",
            font=customtkinter.CTkFont(size=12),
        )
        self.token_label.grid(row=1, column=0, sticky="w", pady=(0, 0), padx=15)

        self.token_options_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.token_options,
            width=130
        )
        self.token_options_combobox.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=15)

        self.delay_label = customtkinter.CTkLabel(
            master=self,
            text="Delay (seconds):",
            font=customtkinter.CTkFont(size=12),
        )
        self.delay_label.grid(row=3, column=0, sticky="w", pady=(0, 0), padx=15)

        self.delay_spinbox = FloatSpinbox(
            master=self,
            step_size=1,
            start_index=1,
        )
        self.delay_spinbox.grid(row=4, column=0, sticky="w", pady=(0, 10), padx=15)

        self.save_to_file_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Save to file",
            checkbox_width=18,
            checkbox_height=18,
            onvalue=True,
            offvalue=False,
        )
        self.save_to_file_checkbox.grid(row=5, column=0, sticky="w", pady=(0, 10), padx=15)

        self.start_button = customtkinter.CTkButton(
            master=self,
            text="Start",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.start_button_event,
        )
        self.start_button.grid(row=6, column=0, sticky="w", pady=15, padx=15)

    @property
    def token_options(self):
        all_tokens = Tokens()._get_all_token_objs()
        return [token.symbol.upper() for token in all_tokens]

    def start_button_event(self):

        wallets = self.right_frame.wallets_table.selected_wallets
        if not wallets:
            messagebox.showerror(
                title="Error",
                message="No wallets selected"
            )
            return

        delay = self.delay_spinbox.get()
        if delay < 0:
            messagebox.showerror(
                title="Error",
                message="Delay must be greater than 0"
            )
            return

        if not isinstance(delay, float):
            messagebox.showerror(
                title="Error",
                message="Delay must be float"
            )
            return

        file_path = None
        if self.save_to_file_checkbox.get():
            file_path = filedialog.asksaveasfilename(
                title="Save wallet balances",
                defaultextension=".xlsx",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
                initialfile="balances.xlsx"
            )
        else:
            yesno = messagebox.askyesno(
                title="Start",
                message="Are you sure you want to start?"
            )
            if not yesno:
                return

        token = self.token_options_combobox.get()
        app_config = Storage().app_config

        checker = BalanceChecker(
            coin_symbol=token,
            base_url=app_config.rpc_url,
        )

        balances = []
        for wallet_data in wallets:
            balance = checker.get_balance_decimals(wallet_data.address)

            balance_data = {
                "wallet_address": wallet_data.address,
                "balance": balance,
            }
            balances.append(balance_data)

        if file_path is not None:
            if self.save_to_file_checkbox.get():
                write_balance_data_to_xlsx(
                    path=file_path,
                    data=balances,
                    coin_option=token
                )
