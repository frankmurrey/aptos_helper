import customtkinter

from src.utils.generate_wallets import generate_keys
from src.schemas.balance_checker import BalanceCheckerConfigSchema

from modules.module_executor import ModuleExecutor

from contracts.tokens import Tokens

from tkinter import (messagebox,
                     filedialog)

from src.storage import Storage


class ToolsTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x600")

        self.generator_label = customtkinter.CTkLabel(self,
                                                      text="Generate aptos keys to file:",
                                                      font=customtkinter.CTkFont(size=14, weight="bold"))
        self.generator_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.wallet_generator_frame = customtkinter.CTkFrame(master=self)
        self.wallet_generator_frame.grid(row=1, column=0, padx=15, sticky="nsew")

        self.wallet_amount_to_generate_label = customtkinter.CTkLabel(self.wallet_generator_frame,
                                                                      text="Amount:")
        self.wallet_amount_to_generate_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.wallet_amount_to_generate_entry = customtkinter.CTkEntry(self.wallet_generator_frame,
                                                                      width=70)
        self.wallet_amount_to_generate_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.generate_aptos_wallets_button = customtkinter.CTkButton(self.wallet_generator_frame,
                                                                     text="Generate",
                                                                     width=70,
                                                                     command=self.generate_button_event)
        self.generate_aptos_wallets_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.balance_checker_label = customtkinter.CTkLabel(self,
                                                            text="Get wallets balances:",
                                                            font=customtkinter.CTkFont(size=14, weight="bold"))
        self.balance_checker_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")

        self.balance_checker_frame = customtkinter.CTkFrame(master=self)
        self.balance_checker_frame.grid(row=3, column=0, padx=15, sticky="nsew")

        self.balance_checker_coin_option_combobox = customtkinter.CTkComboBox(self.balance_checker_frame,
                                                                              width=85,
                                                                              values=self.get_all_token_symbols)
        self.balance_checker_coin_option_combobox.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.delay_entry = customtkinter.CTkEntry(self.balance_checker_frame,
                                                  width=70,
                                                  placeholder_text="Delay sec")
        self.delay_entry.grid(row=0, column=1, padx=0, pady=10, sticky="w")

        self.get_balances_button = customtkinter.CTkButton(self.balance_checker_frame,
                                                           text="Get",
                                                           width=55,
                                                           command=self.check_balance_button_event)
        self.get_balances_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

    def generate_button_event(self):
        amount = self.wallet_amount_to_generate_entry.get()
        if not amount:
            messagebox.showerror("Error", "Amount cannot be empty")
            return
        try:
            amount = int(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        if amount < 1:
            messagebox.showerror("Error", "Amount must be greater than 0")
            return

        keys = generate_keys(amount)

        self.save_keys(keys)

    def save_keys(self, keys):
        file_path = filedialog.asksaveasfilename(title="Save keys",
                                                 defaultextension=".txt",
                                                 filetypes=(("Text files", "*.txt"),),
                                                 initialfile=f"aptos_k.txt")
        if not file_path:
            return

        with open(file_path, "w") as f:
            f.write("\n".join(keys))

        messagebox.showinfo("Success", "Keys saved to {}".format(file_path))

    @property
    def get_all_token_symbols(self):
        all_obj = Tokens().all_tokens
        return [obj.symbol.upper() for obj in all_obj]

    def verify_wallets_amount(self):
        wallets_data = Storage().get_wallets_data()
        if not wallets_data:
            messagebox.showerror("Error", "No wallets provided")
            return False

        aptos_wallets = [wallet.wallet for wallet in wallets_data if wallet.wallet is not None]

        if len(aptos_wallets) == 0:
            messagebox.showerror("Error", "No aptos wallets provided")
            return False

        return True

    def check_balance_button_event(self):
        if self.verify_wallets_amount() is False:
            return

        file_path = filedialog.asksaveasfilename(title="Save wallet balances",
                                                 defaultextension=".xlsx",
                                                 filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*")),
                                                 initialfile="")

        if not file_path:
            return

        current_coin_option = self.balance_checker_coin_option_combobox.get()
        delay = self.delay_entry.get()

        if not delay:
            delay = 1

        config = BalanceCheckerConfigSchema(
            coin_option=current_coin_option,
            min_delay_sec=delay,
            max_delay_sec=delay,
            file_path=file_path
        )

        module_executor = ModuleExecutor(config)
        module_executor.start()




