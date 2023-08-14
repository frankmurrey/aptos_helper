import yaml
import random

import customtkinter

from tkinter import (messagebox,
                     StringVar,
                     filedialog)

from gui.txn_settings_frame import TxnSettingsFrameBlueprint

from src.schemas.pancake import PancakeConfigSchema
from src.schemas.liquidity_swap import LiqSwSwapConfigSchema

from src.route_manager import SwapRouteValidator
from src.storage import Storage

from contracts.tokens import Tokens

from modules.module_executor import ModuleExecutor


class SwapsModule(customtkinter.CTk):

    def __init__(self, tabview):
        super().__init__()

        self.tabview = tabview
        self._tab_name = "Swap"
        self.txn_settings_frame = TxnSettingsFrameBlueprint(self.tabview.tab(self._tab_name))
        self.txn_settings_frame.frame.grid(row=3, column=0, padx=15, pady=(15, 0), sticky="nsew")

        self.data = None
        self.wallets_storage = Storage()
        self.protocol_name = None

        self.swap_protocol_frame = customtkinter.CTkFrame(self.tabview.tab(self._tab_name))
        self.swap_protocol_frame.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="nsew")

        self.swap_protocol_combobox = customtkinter.CTkComboBox(self.swap_protocol_frame,
                                                                values=self.swap_protocol_options,
                                                                command=self.protocol_change_event)

        self.swap_settings_frame = customtkinter.CTkFrame(self.tabview.tab(self._tab_name))
        self.swap_settings_frame.grid(row=2, column=0, padx=15, pady=(15, 0), sticky="nsew")

        self.coin_to_swap_combobox = customtkinter.CTkComboBox(self.swap_settings_frame,
                                                               values=self.coin_to_swap_options,
                                                               command=self.update_coin_combos)

        self.coin_to_receive_combobox = customtkinter.CTkComboBox(self.swap_settings_frame,
                                                                  values=self.coin_to_receive_options())

        self.random_dst_coin_checkbox = customtkinter.CTkCheckBox(self.swap_settings_frame,
                                                                  text="Random dest coin",
                                                                  checkbox_width=18,
                                                                  checkbox_height=18,
                                                                  onvalue=True,
                                                                  offvalue=False,
                                                                  command=self.random_dest_coin_event)

        self.min_amount_entry = customtkinter.CTkEntry(self.swap_settings_frame,
                                                       width=140,
                                                       textvariable=StringVar(value=""))

        self.max_amount_entry = customtkinter.CTkEntry(self.swap_settings_frame,
                                                       width=140,
                                                       textvariable=StringVar(value=""))

        self.send_all_balance_checkbox = customtkinter.CTkCheckBox(self.swap_settings_frame,
                                                                   text="Send all balance",
                                                                   checkbox_width=18,
                                                                   checkbox_height=18,
                                                                   onvalue=True,
                                                                   offvalue=False,
                                                                   command=self.send_all_balance_checkbox_event)

        self.slippage_entry = customtkinter.CTkEntry(self.swap_settings_frame,
                                                     width=140,
                                                     textvariable=StringVar(value="0.5"))

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
        swap_protocol_label = customtkinter.CTkLabel(self.swap_protocol_frame,
                                                     text="Swap protocol:",
                                                     font=customtkinter.CTkFont(size=12, weight="bold"))
        swap_protocol_label.grid(row=0, column=0, padx=(20, 0), pady=(5, 0), sticky="w")
        self.swap_protocol_combobox.grid(row=1, column=0, padx=(20, 0), pady=(0, 15), sticky="w")

    def _add_coin_to_swap_fields(self):
        coin_to_swap_label = customtkinter.CTkLabel(self.swap_settings_frame,
                                                    text="Coin to swap:",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))

        coin_to_swap_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="w")
        self.coin_to_swap_combobox.grid(row=1, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_coin_to_receive_fields(self):
        coin_to_receive_label = customtkinter.CTkLabel(self.swap_settings_frame,
                                                       text="Coin to receive:",
                                                       font=customtkinter.CTkFont(size=12, weight="bold"))

        coin_to_receive_label.grid(row=0, column=1, padx=(30, 0), pady=(10, 0), sticky="w")
        self.coin_to_receive_combobox.grid(row=1, column=1, padx=(30, 0), pady=(0, 0), sticky="w")

    def _add_random_dst_coin_checkbox(self):
        self.random_dst_coin_checkbox.grid(row=2, column=1, padx=(30, 0), pady=(5, 0), sticky="w")

    def _add_min_amount_out_fields(self):
        min_amount_out_label = customtkinter.CTkLabel(self.swap_settings_frame,
                                                      text="Min amount:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_amount_entry.grid(row=4, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def _add_max_amount_out_fields(self):
        max_amount_label = customtkinter.CTkLabel(self.swap_settings_frame,
                                                  text="Max amount:",
                                                  font=customtkinter.CTkFont(size=12, weight="bold"))

        max_amount_label.grid(row=3, column=1, padx=(30, 0), pady=(0, 0), sticky="w")
        self.max_amount_entry.grid(row=4, column=1, padx=(30, 0), pady=(0, 5), sticky="w")

    def _add_send_all_balance_checkbox(self):
        self.send_all_balance_checkbox.grid(row=5, column=0, padx=(20, 0), pady=(0, 15), sticky="w")

    def _add_slippage_fields(self):
        slippage_label = customtkinter.CTkLabel(self.swap_settings_frame,
                                                text="Slippage (%):",
                                                font=customtkinter.CTkFont(size=12, weight="bold"))

        slippage_label.grid(row=6, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.slippage_entry.grid(row=7, column=0, padx=(20, 0), pady=(0, 15), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=4, column=0, padx=(20, 0), pady=(70, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=5, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_save_config_button(self):
        self.save_config_button.grid(row=5, column=0, padx=(210, 0), pady=(15, 0), sticky="w")

    def _add_load_config_button(self):
        self.load_config_button.grid(row=5, column=0, padx=(290, 0), pady=(15, 0), sticky="w")

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

    def random_dest_coin_event(self, ):
        if self.random_dst_coin_checkbox.get() is True:
            self.coin_to_receive_combobox.configure(state="disabled")
        else:
            self.coin_to_receive_combobox.configure(state="normal")

    def send_all_balance_checkbox_event(self):
        checkbox_status = self.send_all_balance_checkbox.get()
        if checkbox_status is True:
            self.min_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""),
                                            fg_color='#3f3f3f')
            self.max_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""),
                                            fg_color='#3f3f3f')
            self.min_amount_entry.configure(state="disabled")
            self.max_amount_entry.configure(state="disabled")
        else:
            self.min_amount_entry.configure(state="normal", placeholder_text="10", fg_color='#343638')
            self.max_amount_entry.configure(state="normal", placeholder_text="20", fg_color='#343638')

    def get_random_dst_coin(self):
        current_protocol = self.swap_protocol_combobox.get()
        if current_protocol == "Pancake":
            protocol_available_coins = self.get_pancake_available_coin_names()
            protocol_available_coins.remove(self.coin_to_swap_combobox.get())

        elif current_protocol == "Liquid Swap":
            protocol_available_coins = self.get_liquid_swap_available_coin_names()
            protocol_available_coins.remove(self.coin_to_swap_combobox.get())

        else:
            protocol_available_coins = []

        if not protocol_available_coins:
            return []

        random_dst_coin = random.choice(protocol_available_coins)
        return random_dst_coin

    def get_values(self):
        swap_protocol = self.swap_protocol_combobox.get()
        if swap_protocol == "Pancake":
            self.data = PancakeConfigSchema()
        elif swap_protocol == "Liquid Swap":
            self.data = LiqSwSwapConfigSchema()
        else:
            messagebox.showerror("Error", "Swap protocol not selected")
            return

        txn_settings = self.txn_settings_frame.get_values()
        self.data.coin_to_swap = self.coin_to_swap_combobox.get()
        self.data.random_dst_coin = self.random_dst_coin_checkbox.get()
        if self.data.random_dst_coin is True:
            self.data.coin_to_receive = self.get_random_dst_coin()
        else:
            self.data.coin_to_receive = self.coin_to_receive_combobox.get()
        self.data.min_amount_out = self.min_amount_entry.get()
        self.data.max_amount_out = self.max_amount_entry.get()
        self.data.send_all_balance = self.send_all_balance_checkbox.get()
        self.data.slippage = self.slippage_entry.get()
        self.data.gas_price = txn_settings["gas_price"]
        self.data.gas_limit = txn_settings["gas_limit"]
        self.data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.data.min_delay_sec = txn_settings["min_delay_sec"]
        self.data.max_delay_sec = txn_settings["max_delay_sec"]
        self.data.txn_wait_timeout_sec = txn_settings["txn_wait_timeout_sec"]
        self.data.wait_for_receipt = txn_settings["wait_for_receipt"]
        self.data.test_mode = self.test_mode_checkbox.get()

        return self.data

    def update_all_fields(self):
        if self.protocol_name:
            self.swap_protocol_combobox.set(self.protocol_name)

        self.coin_to_swap_combobox.set(self.data.coin_to_swap)
        if self.data.random_dst_coin is True:
            self.random_dst_coin_checkbox.select()
            self.coin_to_receive_combobox.configure(state="disabled",)
        else:
            self.random_dst_coin_checkbox.deselect()
            self.coin_to_receive_combobox.configure(state="normal")

        if self.data.send_all_balance is True:
            self.send_all_balance_checkbox.select()
            self.min_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""),
                                            fg_color='#3f3f3f')
            self.max_amount_entry.configure(placeholder_text="",
                                            textvariable=StringVar(value=""),
                                            fg_color='#3f3f3f')
            self.min_amount_entry.configure(state="disabled")
            self.max_amount_entry.configure(state="disabled")
        else:
            self.send_all_balance_checkbox.deselect()
            self.min_amount_entry.configure(state="normal", textvariable=StringVar(value=self.data.min_amount_out),
                                            fg_color='#343638')
            self.max_amount_entry.configure(state="normal", textvariable=StringVar(value=self.data.max_amount_out),
                                            fg_color='#343638')

        self.slippage_entry.configure(textvariable=StringVar(value=self.data.slippage))

        self.txn_settings_frame.gas_price_entry.configure(textvariable=StringVar(value=self.data.gas_price))
        self.txn_settings_frame.gas_limit_entry.configure(textvariable=StringVar(value=self.data.gas_limit))
        if self.data.force_gas_limit is True:
            self.txn_settings_frame.force_gas_limit_checkbox.select()
        else:
            self.txn_settings_frame.force_gas_limit_checkbox.deselect()

        self.txn_settings_frame.min_delay_entry.configure(textvariable=StringVar(value=self.data.min_delay_sec))
        self.txn_settings_frame.max_delay_entry.configure(textvariable=StringVar(value=self.data.max_delay_sec))

        if self.data.wait_for_receipt is True:
            self.txn_settings_frame.wait_for_transaction_checkbox.select()
            self.txn_settings_frame.transaction_wait_time_entry.configure(
                textvariable=StringVar(value=self.data.txn_wait_timeout_sec),
                fg_color='#343638')
        else:
            self.txn_settings_frame.wait_for_transaction_checkbox.deselect()
            self.txn_settings_frame.transaction_wait_time_entry.configure(placeholder_text="",
                                                                          fg_color='#3f3f3f')
            self.txn_settings_frame.transaction_wait_time_entry.configure(state="disabled")
        if self.data.test_mode is True:
            self.test_mode_checkbox.select()
        else:
            self.test_mode_checkbox.deselect()

    def check_config(self):
        route_validator = SwapRouteValidator(self.get_values())
        validation_status = route_validator.check_is_route_valid()
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
        txn_settings = self.txn_settings_frame.get_values()

        self.data.coin_to_swap = self.coin_to_swap_combobox.get()
        self.data.coin_to_receive = self.coin_to_receive_combobox.get()
        self.data.random_dst_coin = self.random_dst_coin_checkbox.get()
        self.data.min_amount_out = float(self.min_amount_entry.get()) if self.send_all_balance_checkbox.get() is False else ""
        self.data.max_amount_out = float(self.max_amount_entry.get()) if self.send_all_balance_checkbox.get() is False else ""
        self.data.send_all_balance = self.send_all_balance_checkbox.get()
        self.data.slippage = float(self.slippage_entry.get())
        self.data.gas_price = float(txn_settings["gas_price"])
        self.data.gas_limit = int(txn_settings["gas_limit"])
        self.data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.data.min_delay_sec = float(txn_settings['min_delay_sec']) if txn_settings['min_delay_sec'].strip(" ") != "" else ""
        self.data.max_delay_sec = float(txn_settings['max_delay_sec']) if txn_settings['min_delay_sec'].strip(" ") != "" else ""
        self.data.txn_wait_timeout_sec = int(txn_settings['txn_wait_timeout_sec']) if txn_settings['txn_wait_timeout_sec'] else ""
        self.data.wait_for_receipt = txn_settings['wait_for_receipt']
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

        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select config",
                                               filetypes=(("YAML files", "*.yaml"), ("all files", "*.*")))
        if file_path == "":
            return

        with open(file_path, "r") as file:
            config_dict = yaml.load(file, Loader=yaml.FullLoader)
        try:
            if config_dict.get("module_name") == "pancake":
                config = PancakeConfigSchema(**config_dict)
                swap_protocol = "Pancake"

            elif config_dict.get("module_name") == "liquidityswap_swap":
                config = LiqSwSwapConfigSchema(**config_dict)
                swap_protocol = "Liquid Swap"

            else:
                messagebox.showerror("Error", "Swap protocol not selected")
                return

            self.protocol_name = swap_protocol
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
        self._add_random_dst_coin_checkbox()
        self._add_min_amount_out_fields()
        self._add_max_amount_out_fields()
        self._add_send_all_balance_checkbox()
        self._add_slippage_fields()
        self._add_next_button()
        self._add_test_mode_checkbox()
        self._add_save_config_button()
        self._add_load_config_button()
