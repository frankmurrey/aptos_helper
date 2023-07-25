import yaml

import customtkinter

from tkinter import (messagebox,
                     StringVar,
                     filedialog)

from src.schemas.pancake import PancakeConfigSchema
from src.schemas.liquidity_swap import LiqSwSwapConfigSchema

from src.route_manager import SwapRouteValidator
from src.storage import WalletsStorage

from contracts.tokens import Tokens

from modules.module_executor import ModuleExecutor


class SwapsModule(customtkinter.CTk):

    def __init__(self, tabview):
        super().__init__()

        self.tabview = tabview
        self._tab_name = "Swap"
        self.data = None
        self.wallets_storage = WalletsStorage()

        self.swap_protocol_combobox = customtkinter.CTkComboBox(self.tabview.tab(self._tab_name),
                                                                values=self.swap_protocol_options,
                                                                command=self.protocol_change_event)

        self.coin_to_swap_combobox = customtkinter.CTkComboBox(self.tabview.tab(self._tab_name),
                                                               values=self.coin_to_swap_options,
                                                               command=self.update_coin_combos)

        self.coin_to_receive_combobox = customtkinter.CTkComboBox(self.tabview.tab(self._tab_name),
                                                                  values=self.coin_to_receive_options(),
                                                                  command=self.update_coin_combos)

        self.min_amount_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                       width=140,
                                                       placeholder_text="10")

        self.max_amount_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                       width=140,
                                                       placeholder_text="20")

        self.send_all_balance_checkbox = customtkinter.CTkCheckBox(self.tabview.tab(self._tab_name),
                                                                   text="Send all balance",
                                                                   checkbox_width=18,
                                                                   checkbox_height=18,
                                                                   onvalue=True,
                                                                   offvalue=False,
                                                                   command=self.send_all_balance_checkbox_event)

        self.empty_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                  text="",
                                                  font=customtkinter.CTkFont(size=12, weight="bold"))

        self.gas_price_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=70)

        self.gas_limit_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=70)

        self.slippage_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                     width=70,
                                                     textvariable=StringVar(value="0.5"))

        self.min_delay_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=140,
                                                      textvariable=StringVar(value="20"))

        self.max_delay_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=140,
                                                      textvariable=StringVar(value="40"))

        self.wait_for_transaction_checkbox = customtkinter.CTkCheckBox(self.tabview.tab(self._tab_name),
                                                                       text="Wait for transaction",
                                                                       checkbox_width=18,
                                                                       checkbox_height=18,
                                                                       onvalue=True,
                                                                       offvalue=False,
                                                                       command=self.wait_for_transaction_checkbox_event)

        self.transaction_wait_time_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                                  width=140,
                                                                  state="disabled")

        self.next_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                   text="Start",
                                                   width=140,
                                                   command=self.next_button_event)

        self.test_mode_checkbox = customtkinter.CTkCheckBox(self.tabview.tab(self._tab_name),
                                                            text="Test mode",
                                                            checkbox_width=18,
                                                            checkbox_height=18,
                                                            onvalue=True,
                                                            offvalue=False)

        self.save_config_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                          text="Save cfg",
                                                          width=70,
                                                          command=self.save_config_event)

        self.load_config_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                          text="Load cfg",
                                                          width=70,
                                                          command=self.load_config_event)

    def _add_swap_protocol_fields(self):
        swap_protocol_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                        text="Swap protocol:",
                                                        font=customtkinter.CTkFont(size=12, weight="bold"))
        swap_protocol_label.grid(row=0, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.swap_protocol_combobox.grid(row=1, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_coin_to_swap_fields(self):
        coin_to_swap_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                    text="Coin to swap:",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))

        coin_to_swap_label.grid(row=2, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.coin_to_swap_combobox.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_coin_to_receive_fields(self):
        coin_to_receive_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                       text="Coin to receive:",
                                                       font=customtkinter.CTkFont(size=12, weight="bold"))

        coin_to_receive_label.grid(row=2, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        self.coin_to_receive_combobox.grid(row=3, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_min_amount_out_fields(self):
        min_amount_out_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                      text="Min amount:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=4, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_amount_entry.grid(row=5, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_max_amount_out_fields(self):
        max_amount_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                  text="Max amount:",
                                                  font=customtkinter.CTkFont(size=12, weight="bold"))

        max_amount_label.grid(row=4, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        self.max_amount_entry.grid(row=5, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_send_all_balance_checkbox(self):
        self.send_all_balance_checkbox.grid(row=6, column=0, padx=(20, 0), pady=(5, 0), sticky="w")

    def _add_empty_label(self):
        self.empty_label.grid(row=7, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_gas_price_fields(self):
        gas_price_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Gas price:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        gas_price_label.grid(row=8, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.gas_price_entry.grid(row=9, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_gas_limit_fields(self):
        gas_limit_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Gas limit:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        gas_limit_label.grid(row=8, column=0, padx=(105, 0), pady=(0, 0), sticky="w")
        self.gas_limit_entry.grid(row=9, column=0, padx=(105, 0), pady=(0, 0), sticky="w")

    def _add_slippage_fields(self):
        slippage_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                text="Slippage %:",
                                                font=customtkinter.CTkFont(size=12, weight="bold"))

        slippage_label.grid(row=10, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.slippage_entry.grid(row=11, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_min_delay_fields(self):
        min_delay_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Min delay (sec):",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        min_delay_label.grid(row=12, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_delay_entry.grid(row=13, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_max_delay_fields(self):
        max_delay_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Max delay (sec):",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        max_delay_label.grid(row=12, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        self.max_delay_entry.grid(row=13, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_transaction_wait_time_entry(self):
        transaction_wait_time_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                             text="Transaction wait time (sec):",
                                                             font=customtkinter.CTkFont(size=12, weight="bold"))

        transaction_wait_time_label.grid(row=14, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.transaction_wait_time_entry.grid(row=15, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_wait_for_transaction_checkbox(self):
        self.wait_for_transaction_checkbox.grid(row=16, column=0, padx=(20, 0), pady=(5, 0), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=17, column=0, padx=(20, 0), pady=(95, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=18, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_save_config_button(self):
        self.save_config_button.grid(row=18, column=1, padx=(0, 0), pady=(15, 0), sticky="w")

    def _add_load_config_button(self):
        self.load_config_button.grid(row=18, column=1, padx=(80, 0), pady=(15, 0), sticky="w")

    def get_pancake_available_coin_names(self):
        pancake_coins = Tokens().get_pancake_available_coins()
        pancake_coin_names = [coin.symbol.upper() for coin in pancake_coins]
        return pancake_coin_names

    def get_liquid_swap_available_coin_names(self):
        liquid_swap_coins = Tokens().get_liquid_swap_available_coins()
        liquid_swap_coin_names = [coin.symbol.upper() for coin in liquid_swap_coins]
        return liquid_swap_coin_names

    @property
    def coin_to_swap_options(self):
        current_swap_protocol = self.swap_protocol_combobox.get()
        if current_swap_protocol == "Pancake":
            protocol_available_coins = self.get_pancake_available_coin_names()

        elif current_swap_protocol == "Liquid Swap":
            protocol_available_coins = self.get_liquid_swap_available_coin_names()

        else:
            protocol_available_coins = []

        return protocol_available_coins

    @property
    def swap_protocol_options(self):
        return ["Pancake", "Liquid Swap"]

    def coin_to_receive_options(self):
        coin_to_swap = self.coin_to_swap_combobox.get()

        current_protocol = self.swap_protocol_combobox.get()
        if current_protocol == "Pancake":
            protocol_available_coins = self.get_pancake_available_coin_names()

        elif current_protocol == "Liquid Swap":
            protocol_available_coins = self.get_liquid_swap_available_coin_names()

        else:
            protocol_available_coins = []

        if not protocol_available_coins:
            return []

        current_protocol_coin_names = [coin.upper() for coin in protocol_available_coins]
        current_protocol_coin_names.remove(coin_to_swap)

        return current_protocol_coin_names

    def protocol_change_event(self, *args):
        self.coin_to_swap_combobox.configure(values=self.coin_to_swap_options)
        self.coin_to_swap_combobox.set(self.coin_to_swap_options[0])
        self.coin_to_receive_combobox.configure(values=self.coin_to_receive_options())
        self.coin_to_receive_combobox.set(self.coin_to_receive_options()[0])

    def update_coin_combos(self, *args):
        self.coin_to_swap_combobox.configure(values=self.coin_to_swap_options)
        self.coin_to_receive_combobox.configure(values=self.coin_to_receive_options())
        self.coin_to_receive_combobox.set(self.coin_to_receive_options()[0])

    def send_all_balance_checkbox_event(self):
        checkbox_status = self.send_all_balance_checkbox.get()
        if checkbox_status is True:
            self.min_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""))
            self.max_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""))
            self.min_amount_entry.configure(state="disabled")
            self.max_amount_entry.configure(state="disabled")
        else:
            self.min_amount_entry.configure(state="normal", placeholder_text="10")
            self.max_amount_entry.configure(state="normal", placeholder_text="20")

    def wait_for_transaction_checkbox_event(self):
        checkbox_status = self.wait_for_transaction_checkbox.get()
        if checkbox_status is True:
            self.transaction_wait_time_entry.configure(state="normal", placeholder_text="120")
        else:
            self.transaction_wait_time_entry.configure(placeholder_text="")
            self.transaction_wait_time_entry.configure(state="disabled")

    def get_values(self):
        swap_protocol = self.swap_protocol_combobox.get()
        if swap_protocol == "Pancake":
            self.data = PancakeConfigSchema()
        elif swap_protocol == "Liquid Swap":
            self.data = LiqSwSwapConfigSchema()
        else:
            messagebox.showerror("Error", "Swap protocol not selected")
            return

        self.data.coin_to_swap = self.coin_to_swap_combobox.get()
        self.data.coin_to_receive = self.coin_to_receive_combobox.get()
        self.data.min_amount_out = self.min_amount_entry.get()
        self.data.max_amount_out = self.max_amount_entry.get()
        self.data.send_all_balance = self.send_all_balance_checkbox.get()
        self.data.gas_price = self.gas_price_entry.get()
        self.data.gas_limit = self.gas_limit_entry.get()
        self.data.slippage = self.slippage_entry.get()
        self.data.min_delay_sec = self.min_delay_entry.get()
        self.data.max_delay_sec = self.max_delay_entry.get()
        self.data.txn_wait_timeout_sec = self.transaction_wait_time_entry.get()
        self.data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.data.test_mode = self.test_mode_checkbox.get()

        return self.data

    def update_all_fields(self):
        self.coin_to_swap_combobox.set(self.data.coin_to_swap)
        self.coin_to_receive_combobox.set(self.data.coin_to_receive)

        if self.data.send_all_balance is True:
            self.send_all_balance_checkbox.select()
            self.min_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""))
            self.max_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""))
            self.min_amount_entry.configure(state="disabled")
            self.max_amount_entry.configure(state="disabled")
        else:
            self.send_all_balance_checkbox.deselect()
            self.min_amount_entry.configure(state="normal", textvariable=StringVar(value=self.data.min_amount_out))
            self.max_amount_entry.configure(state="normal", textvariable=StringVar(value=self.data.max_amount_out))

        self.gas_price_entry.configure(textvariable=StringVar(value=self.data.gas_price))
        self.gas_limit_entry.configure(textvariable=StringVar(value=self.data.gas_limit))
        self.slippage_entry.configure(textvariable=StringVar(value=self.data.slippage))

        self.min_delay_entry.configure(textvariable=StringVar(value=self.data.min_delay_sec))
        self.max_delay_entry.configure(textvariable=StringVar(value=self.data.max_delay_sec))

        if self.data.wait_for_receipt is True:
            self.wait_for_transaction_checkbox.select()
            self.transaction_wait_time_entry.configure(textvariable=StringVar(value=self.data.txn_wait_timeout_sec))
        else:
            self.wait_for_transaction_checkbox.deselect()
            self.transaction_wait_time_entry.configure(placeholder_text="")
            self.transaction_wait_time_entry.configure(state="disabled")
        if self.data.test_mode is True:
            self.test_mode_checkbox.select()
        else:
            self.test_mode_checkbox.deselect()

    def check_config(self):
        route_validator = SwapRouteValidator(self.get_values())
        validation_status = route_validator.validate()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_config(self):
        pre_build_status = self.check_config()
        if pre_build_status is not True:
            return

        swap_protocol = self.swap_protocol_combobox.get()
        if swap_protocol == "Pancake":
            self.data = PancakeConfigSchema()
        elif swap_protocol == "Liquid Swap":
            self.data = LiqSwSwapConfigSchema()
        else:
            messagebox.showerror("Error", "Swap protocol not selected")
            return

        self.data.coin_to_swap = self.coin_to_swap_combobox.get()
        self.data.coin_to_receive = self.coin_to_receive_combobox.get()
        self.data.min_amount_out = float(self.min_amount_entry.get()) if self.send_all_balance_checkbox.get() is False else ""
        self.data.max_amount_out = float(self.max_amount_entry.get()) if self.send_all_balance_checkbox.get() is False else ""
        self.data.send_all_balance = self.send_all_balance_checkbox.get()
        self.data.gas_price = float(self.gas_price_entry.get())
        self.data.gas_limit = int(self.gas_limit_entry.get())
        self.data.slippage = float(self.slippage_entry.get())
        self.data.min_delay_sec = float(self.min_delay_entry.get()) if self.min_delay_entry.get().strip(" ") != "" else ""
        self.data.max_delay_sec = float(self.max_delay_entry.get()) if self.min_delay_entry.get().strip(" ") != "" else ""
        self.data.txn_wait_timeout_sec = int(self.transaction_wait_time_entry.get()) if self.wait_for_transaction_checkbox.get() else ""
        self.data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.data.test_mode = self.test_mode_checkbox.get()

        return self.data

    def save_config_event(self):
        pre_build_status = self.check_config()
        if pre_build_status is not True:
            return
        config = self.get_values()

        config_dict = config.model_dump()
        file_path = filedialog.asksaveasfilename(defaultextension=".yaml",
                                                 initialdir=".",
                                                 title="Save config",
                                                 filetypes=(("YAML files", "*.yaml"), ("all files", "*.*")),
                                                 initialfile=f"{config.module_name}_config.yaml")

        if file_path == "":
            return

        with open(file_path, "w") as file:
            yaml.dump(config_dict, file)

    def load_config_event(self):
        swap_protocol = self.swap_protocol_combobox.get()

        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select config",
                                               filetypes=(("YAML files", "*.yaml"), ("all files", "*.*")))
        if file_path == "":
            return

        with open(file_path, "r") as file:
            config_dict = yaml.load(file, Loader=yaml.FullLoader)
        try:
            if swap_protocol == "Pancake":
                config = PancakeConfigSchema(**config_dict)
                if config.module_name != "pancake":
                    messagebox.showerror("Error", f"Wrong config file selected, current module is <pancake>,"
                                                  f" selected module is <{config.module_name}>")
                    return
            elif swap_protocol == "Liquid Swap":
                config = LiqSwSwapConfigSchema(**config_dict)
                if config.module_name != "liquidityswap_swap":
                    messagebox.showerror("Error", f"Wrong config file selected, current module is <liquidity_swap>,"
                                                  f" selected module is <{config.module_name}>")
                    return
            else:
                messagebox.showerror("Error", "Swap protocol not selected")
                return

            self.data = config
            self.update_all_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Wrong config file selected, error: {e}")

    def verify_wallets_amount(self):
        wallets_data = self.wallets_storage.get_wallets_data()
        if not wallets_data:
            messagebox.showerror("Error", "No wallets provided")
            return False

        aptos_wallets = [wallet.wallet for wallet in wallets_data if wallet.wallet is not None]

        if len(aptos_wallets) == 0:
            messagebox.showerror("Error", "No aptos wallets provided")
            return False

        return True

    def next_button_event(self):
        config = self.build_config()
        if config is None:
            return

        if not self.verify_wallets_amount():
            return

        yesno = messagebox.askyesno("Warning", "Are you sure you want to start?\n"
                                               "Check all params carefully, if ready smash YES.")
        if yesno is False:
            return
        module_executor = ModuleExecutor(config)
        module_executor.start()

    def add_all_fields(self):
        self._add_swap_protocol_fields()
        self._add_coin_to_swap_fields()
        self._add_coin_to_receive_fields()
        self._add_min_amount_out_fields()
        self._add_max_amount_out_fields()
        self._add_send_all_balance_checkbox()
        self._add_empty_label()
        self._add_gas_price_fields()
        self._add_gas_limit_fields()
        self._add_slippage_fields()
        self._add_min_delay_fields()
        self._add_max_delay_fields()
        self._add_transaction_wait_time_entry()
        self._add_wait_for_transaction_checkbox()
        self._add_next_button()
        self._add_test_mode_checkbox()
        self._add_save_config_button()
        self._add_load_config_button()