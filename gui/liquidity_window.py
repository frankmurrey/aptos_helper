import yaml

import customtkinter
from tkinter import (messagebox,
                     StringVar,
                     filedialog
)
from src.schemas.thala import (ThalaAddLiquidityConfigSchema,
                               ThalaRemoveLiquidityConfigSchema)
from src.schemas.liquidity_swap import (LiqSwAddLiquidityConfigSchema,
                                        LiqSwRemoveLiquidityConfigSchema)
from src.route_manager import (AddLiquidityConfigValidator,
                               RemoveLiquidityConfigValidator)
from src.storage import WalletsStorage

from contracts.tokens import Tokens

from modules.module_executor import ModuleExecutor


class Liquidity(customtkinter.CTk):
    add_liquidity_config: ThalaAddLiquidityConfigSchema
    remove_liquidity_config: ThalaRemoveLiquidityConfigSchema

    def __init__(self, tabview):
        super().__init__()
        self.tabview = tabview
        self._tab_name = "Liquidity"
        self.add_liq_data = None
        self.remove_liq_data = None
        self.wallets_storage = WalletsStorage()

        self.liquidity_protocol_combobox = customtkinter.CTkComboBox(self.tabview.tab(self._tab_name),
                                                                     values=self.protocol_options,
                                                                     command=self.protocol_change_event)

        self.add_liquidity_frame = customtkinter.CTkFrame(master=self.tabview.tab(self._tab_name))
        self.add_liquidity_frame.grid(row=2, column=0, padx=15, pady=(10, 0), sticky="nsew")

        self.add_liq_switch = customtkinter.CTkSwitch(self.add_liquidity_frame,
                                                      text="Add Liquidity",
                                                      font=customtkinter.CTkFont(size=15, weight="bold"),
                                                      text_color="#6fc276",
                                                      onvalue=True,
                                                      offvalue=False,
                                                      command=self.add_switch_event)

        self.coin_x_combobox = customtkinter.CTkComboBox(self.add_liquidity_frame,
                                                         values=self._coin_x_options,
                                                         command=self.update_coin_options)

        self.coin_y_combobox = customtkinter.CTkComboBox(self.add_liquidity_frame,
                                                         values=self._coin_y_options)

        self.min_amount_out_entry = customtkinter.CTkEntry(self.add_liquidity_frame,
                                                           width=140,
                                                           placeholder_text="10")

        self.max_amount_out_entry = customtkinter.CTkEntry(self.add_liquidity_frame,
                                                           width=140,
                                                           placeholder_text="20")

        self.send_all_balance_checkbox = customtkinter.CTkCheckBox(self.add_liquidity_frame,
                                                                   text="Send all balance",
                                                                   checkbox_width=18,
                                                                   checkbox_height=18,
                                                                   onvalue=True,
                                                                   offvalue=False,
                                                                   command=self.send_all_balance_checkbox_event)

        self.remove_liquidity_frame = customtkinter.CTkFrame(master=self.tabview.tab(self._tab_name))
        self.remove_liquidity_frame.grid(row=3, column=0, padx=15, pady=(15, 0), sticky="nsew")

        self.remove_liq_switch = customtkinter.CTkSwitch(self.remove_liquidity_frame,
                                                         text="Remove Liquidity",
                                                         font=customtkinter.CTkFont(size=15, weight="bold"),
                                                         text_color="#F47174",
                                                         onvalue=True,
                                                         offvalue=False,
                                                         command=self.remove_switch_event)

        self.coin_x2_combobox = customtkinter.CTkComboBox(self.remove_liquidity_frame,
                                                          values=self._coin_x_options,
                                                          command=self.update_coin_options2)

        self.coin_y2_combobox = customtkinter.CTkComboBox(self.remove_liquidity_frame,
                                                          values=self._coin_y2_options)

        self.common_settings_frame = customtkinter.CTkFrame(master=self.tabview.tab(self._tab_name))
        self.common_settings_frame.grid(row=4, column=0, padx=15, pady=(15, 0), sticky="nsew")

        self.common_settings_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                            text="Common Settings",
                                                            font=customtkinter.CTkFont(size=15, weight="bold"),
                                                            text_color="#99CCFF")

        self.gas_price_entry = customtkinter.CTkEntry(self.common_settings_frame,
                                                      width=70,
                                                      textvariable=StringVar(value="100"))

        self.gas_limit_entry = customtkinter.CTkEntry(self.common_settings_frame,
                                                      width=70)

        self.min_delay_entry = customtkinter.CTkEntry(self.common_settings_frame,
                                                      width=140,
                                                      textvariable=StringVar(value="20"))

        self.max_delay_entry = customtkinter.CTkEntry(self.common_settings_frame,
                                                      width=140,
                                                      textvariable=StringVar(value="40"))

        self.wait_for_transaction_checkbox = customtkinter.CTkCheckBox(self.common_settings_frame,
                                                                       text="Wait for transaction",
                                                                       checkbox_width=18,
                                                                       checkbox_height=18,
                                                                       onvalue=True,
                                                                       offvalue=False,
                                                                       command=self.wait_for_transaction_checkbox_event)

        self.transaction_wait_time_entry = customtkinter.CTkEntry(self.common_settings_frame,
                                                                  width=140,
                                                                  state="disabled")

        self.test_mode_checkbox = customtkinter.CTkCheckBox(self.tabview.tab(self._tab_name),
                                                            text="Test mode",
                                                            checkbox_width=18,
                                                            checkbox_height=18,
                                                            onvalue=True,
                                                            offvalue=False)

        self.next_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                   text="Start",
                                                   width=140,
                                                   command=self.next_button_event)

        self.save_config_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                          text="Save cfg",
                                                          width=70,
                                                          command=self.save_config_event)

        self.load_config_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                          text="Load cfg",
                                                          width=70)

    def _add_liquidity_protocol_fields(self):
        liquidity_protocol_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                          text="Liquidity protocol:",
                                                          font=customtkinter.CTkFont(size=12, weight="bold"))
        liquidity_protocol_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="w")
        self.liquidity_protocol_combobox.grid(row=1, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def add_add_liq_switch(self):
        self.add_liq_switch.grid(row=2, column=0, padx=(20, 0), pady=(10, 0), sticky="w")

    def _add_coin_x_fields(self):
        coin_x_label = customtkinter.CTkLabel(self.add_liquidity_frame,
                                              text="Coin X",
                                              font=customtkinter.CTkFont(size=12, weight="bold"))
        coin_x_label.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.coin_x_combobox.grid(row=4, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_coin_y_fields(self):
        coin_y_label = customtkinter.CTkLabel(self.add_liquidity_frame,
                                              text="Coin Y",
                                              font=customtkinter.CTkFont(size=12, weight="bold"))
        coin_y_label.grid(row=3, column=1, padx=(30, 0), pady=(0, 0), sticky="w")
        self.coin_y_combobox.grid(row=4, column=1, padx=(30, 0), pady=(0, 0), sticky="e")

    def _add_min_amount_out_entry(self):
        min_amount_out_label = customtkinter.CTkLabel(self.add_liquidity_frame,
                                                      text="Min amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=5, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_amount_out_entry.grid(row=6, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def _add_max_amount_out_entry(self):
        max_amount_out_label = customtkinter.CTkLabel(self.add_liquidity_frame,
                                                      text="Max amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        max_amount_out_label.grid(row=5, column=1, padx=(30, 0), pady=(0, 0), sticky="w")
        self.max_amount_out_entry.grid(row=6, column=1, padx=(30, 0), pady=(0, 10), sticky="e")

    def _add_send_all_balance_checkbox(self):
        self.send_all_balance_checkbox.grid(row=7, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def _add_remove_liq_switch(self):
        self.remove_liq_switch.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="w")

    def _add_coin_x2_fields(self):
        coin_x2_label = customtkinter.CTkLabel(self.remove_liquidity_frame,
                                               text="Coin X",
                                               font=customtkinter.CTkFont(size=12, weight="bold"))
        coin_x2_label.grid(row=1, column=0, padx=(20, 0), sticky="w")
        self.coin_x2_combobox.grid(row=2, column=0, padx=(20, 0), pady=(0, 20), sticky="w")

    def _add_coin_y2_fields(self):
        coin_y2_label = customtkinter.CTkLabel(self.remove_liquidity_frame,
                                               text="Coin Y",
                                               font=customtkinter.CTkFont(size=12, weight="bold"))
        coin_y2_label.grid(row=1, column=1, sticky="w", padx=(0, 20))
        self.coin_y2_combobox.grid(row=2, column=1, padx=(0, 20), pady=(0, 20), sticky="w")

    def _add_common_settings_label_fields(self):
        self.common_settings_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="w")

    def _add_gas_price_entry(self):
        gas_price_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                 text="Gas price:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        gas_price_label.grid(row=1, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.gas_price_entry.grid(row=2, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_gas_limit_entry(self):
        gas_limit_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                 text="Gas limit:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        gas_limit_label.grid(row=1, column=0, padx=(105, 0), pady=(0, 0), sticky="w")
        self.gas_limit_entry.grid(row=2, column=0, padx=(105, 0), pady=(0, 0), sticky="w")

    def _add_min_delay_entry(self):
        min_delay_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                 text="Min delay:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        min_delay_label.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_delay_entry.grid(row=4, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_max_delay_entry(self):
        max_delay_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                 text="Max delay:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        max_delay_label.grid(row=3, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        self.max_delay_entry.grid(row=4, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_transaction_wait_time_entry(self):
        transaction_wait_time_label = customtkinter.CTkLabel(self.common_settings_frame,
                                                             text="Transaction wait time (sec):",
                                                             font=customtkinter.CTkFont(size=12, weight="bold"))

        transaction_wait_time_label.grid(row=5, column=0, padx=(20, 0), sticky="w")
        self.transaction_wait_time_entry.grid(row=6, column=0, padx=(20, 0), pady=(0, 5), sticky="w")

    def _add_wait_for_transaction_checkbox(self):
        self.wait_for_transaction_checkbox.grid(row=7, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=8, column=0, padx=(20, 0), pady=(50, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=9, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    @property
    def _coin_x_options(self):
        current_protocol = self.liquidity_protocol_combobox.get()
        if current_protocol == "Liquid Swap":
            available_tokens = Tokens().get_liquid_swap_available_coins()
        elif current_protocol == "Thala":
            available_tokens = Tokens().get_thala_available_coins()
        else:
            raise Exception(f"Unknown protocol: {current_protocol}")

        return [token.symbol.upper() for token in available_tokens]

    @property
    def _coin_y_options(self):
        coin_x1 = self.coin_x_combobox.get()

        current_protocol = self.liquidity_protocol_combobox.get()
        if current_protocol == "Liquid Swap":
            available_tokens = Tokens().get_liquid_swap_available_coins()
            protocol_available_coins = [token.symbol.upper() for token in available_tokens]

        elif current_protocol == "Thala":
            available_tokens = Tokens().get_thala_available_coins()
            protocol_available_coins = [token.symbol.upper() for token in available_tokens]

        else:
            protocol_available_coins = []

        if not protocol_available_coins:
            return []

        current_protocol_coin_names = [coin.upper() for coin in protocol_available_coins]
        current_protocol_coin_names.remove(coin_x1)

        return current_protocol_coin_names

    @property
    def _coin_y2_options(self):
        coin_x2 = self.coin_x2_combobox.get()

        current_protocol = self.liquidity_protocol_combobox.get()
        if current_protocol == "Liquid Swap":
            available_tokens = Tokens().get_liquid_swap_available_coins()
            protocol_available_coins = [token.symbol.upper() for token in available_tokens]

        elif current_protocol == "Thala":
            available_tokens = Tokens().get_thala_available_coins()
            protocol_available_coins = [token.symbol.upper() for token in available_tokens]

        else:
            protocol_available_coins = []

        if not protocol_available_coins:
            return []

        current_protocol_coin_names = [coin.upper() for coin in protocol_available_coins]
        current_protocol_coin_names.remove(coin_x2)

        return current_protocol_coin_names

    @property
    def protocol_options(self):
        return ["Liquid Swap", "Thala"]

    def protocol_change_event(self, event):
        self.coin_x_combobox.configure(values=self._coin_x_options)
        self.coin_x_combobox.set(self._coin_x_options[0])
        self.coin_y_combobox.configure(values=self._coin_y_options)
        self.coin_y_combobox.set(self._coin_y_options[0])

        self.coin_x2_combobox.configure(values=self._coin_x_options)
        self.coin_x2_combobox.set(self._coin_x_options[0])
        self.coin_y2_combobox.configure(values=self._coin_y_options)
        self.coin_y2_combobox.set(self._coin_y_options[0])

    def update_coin_options(self, event):
        self.coin_x_combobox.configure(values=self._coin_x_options)
        self.coin_y_combobox.configure(values=self._coin_y_options)
        self.coin_y_combobox.set(self._coin_y_options[0])

    def update_coin_options2(self, event):
        self.coin_x2_combobox.configure(values=self._coin_x_options)
        self.coin_y2_combobox.configure(values=self._coin_y2_options)
        self.coin_y2_combobox.set(self._coin_y2_options[0])

    def send_all_balance_checkbox_event(self):
        checkbox_status = self.send_all_balance_checkbox.get()
        if checkbox_status is True:
            self.min_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""))
            self.max_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""))
            self.min_amount_out_entry.configure(state="disabled")
            self.max_amount_out_entry.configure(state="disabled")
        else:
            self.min_amount_out_entry.configure(state="normal", placeholder_text="10")
            self.max_amount_out_entry.configure(state="normal", placeholder_text="20")

    def wait_for_transaction_checkbox_event(self):
        checkbox_status = self.wait_for_transaction_checkbox.get()
        if checkbox_status is True:
            self.transaction_wait_time_entry.configure(state="normal", placeholder_text="120")
        else:
            self.transaction_wait_time_entry.configure(placeholder_text="")
            self.transaction_wait_time_entry.configure(state="disabled")

    def add_switch_event(self):
        status = self.add_liq_switch.get()

        if status is True:
            self.coin_x2_combobox.configure(state="disabled")
            self.coin_y2_combobox.configure(state="disabled")
            self.remove_liq_switch.deselect()
            self.remove_liq_switch.configure(state="disabled")
        else:
            self.coin_x2_combobox.configure(state="normal")
            self.coin_y2_combobox.configure(state="normal")
            self.remove_liq_switch.configure(state="normal")

    def remove_switch_event(self):
        status = self.remove_liq_switch.get()

        if status is True:
            self.coin_x_combobox.configure(state="disabled")
            self.coin_y_combobox.configure(state="disabled")
            self.min_amount_out_entry.configure(state="disabled")
            self.max_amount_out_entry.configure(state="disabled")
            self.send_all_balance_checkbox.deselect()
            self.send_all_balance_checkbox.configure(state="disabled")
            self.add_liq_switch.deselect()
            self.add_liq_switch.configure(state="disabled")
        else:
            self.coin_x_combobox.configure(state="normal")
            self.coin_y_combobox.configure(state="normal")
            self.min_amount_out_entry.configure(state="normal")
            self.max_amount_out_entry.configure(state="normal")
            self.send_all_balance_checkbox.configure(state="normal")
            self.add_liq_switch.configure(state="normal")

    def get_current_remove_liq_data_schema(self):
        swap_protocol = self.liquidity_protocol_combobox.get()
        if swap_protocol == "Liquid Swap":
            remove_liq_data = LiqSwRemoveLiquidityConfigSchema()
        elif swap_protocol == "Thala":
            remove_liq_data = ThalaRemoveLiquidityConfigSchema()
        else:
            messagebox.showerror("Error", "Protocol not selected")
            return

        return remove_liq_data

    def get_current_add_liq_data_schema(self):
        swap_protocol = self.liquidity_protocol_combobox.get()
        if swap_protocol == "Liquid Swap":
            remove_liq_data = LiqSwAddLiquidityConfigSchema()
        elif swap_protocol == "Thala":
            remove_liq_data = ThalaAddLiquidityConfigSchema()
        else:
            messagebox.showerror("Error", "Protocol not selected")
            return

        return remove_liq_data

    def get_remove_liq_values(self):
        self.remove_liq_data = self.get_current_remove_liq_data_schema()

        self.remove_liq_data.coin_x = self.coin_x2_combobox.get()
        self.remove_liq_data.coin_y = self.coin_y2_combobox.get()
        self.remove_liq_data.gas_price = self.gas_price_entry.get()
        self.remove_liq_data.gas_limit = self.gas_limit_entry.get()
        self.remove_liq_data.min_delay_sec = self.min_delay_entry.get()
        self.remove_liq_data.max_delay_sec = self.max_delay_entry.get()
        self.remove_liq_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.remove_liq_data.txn_wait_timeout_sec = self.transaction_wait_time_entry.get()
        self.remove_liq_data.test_mode = self.test_mode_checkbox.get()

        return self.remove_liq_data

    def check_remove_liq_config(self):
        route_validator = RemoveLiquidityConfigValidator(self.get_remove_liq_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_remove_liq_config(self):
        pre_build_status = self.check_remove_liq_config()
        if pre_build_status is not True:
            return
        self.remove_liq_data = self.get_current_remove_liq_data_schema()

        self.remove_liq_data.coin_x = self.coin_x2_combobox.get()
        self.remove_liq_data.coin_y = self.coin_y2_combobox.get()
        self.remove_liq_data.gas_price = int(self.gas_price_entry.get())
        self.remove_liq_data.gas_limit = int(self.gas_limit_entry.get())
        self.remove_liq_data.min_delay_sec = float(self.min_delay_entry.get())
        self.remove_liq_data.max_delay_sec = float(self.max_delay_entry.get())
        self.remove_liq_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.remove_liq_data.txn_wait_timeout_sec = int(self.transaction_wait_time_entry.get() if self.remove_liq_data.wait_for_receipt else 0)
        self.remove_liq_data.test_mode = self.test_mode_checkbox.get()

        return self.remove_liq_data

    def get_add_liq_values(self):
        self.add_liq_data = self.get_current_add_liq_data_schema()

        self.add_liq_data.coin_x = self.coin_x_combobox.get()
        self.add_liq_data.coin_y = self.coin_y_combobox.get()
        self.add_liq_data.min_amount_out = self.min_amount_out_entry.get()
        self.add_liq_data.max_amount_out = self.max_amount_out_entry.get()
        self.add_liq_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.add_liq_data.gas_price = self.gas_price_entry.get()
        self.add_liq_data.gas_limit = self.gas_limit_entry.get()
        self.add_liq_data.min_delay_sec = self.min_delay_entry.get()
        self.add_liq_data.max_delay_sec = self.max_delay_entry.get()
        self.add_liq_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.add_liq_data.txn_wait_timeout_sec = self.transaction_wait_time_entry.get()
        self.add_liq_data.test_mode = self.test_mode_checkbox.get()

        return self.add_liq_data

    def check_add_liq_config(self):
        route_validator = AddLiquidityConfigValidator(self.get_add_liq_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_add_liq_config(self):
        pre_build_status = self.check_add_liq_config()
        if pre_build_status is not True:
            return

        self.add_liq_data = self.get_current_add_liq_data_schema()

        self.add_liq_data.coin_x = self.coin_x_combobox.get()
        self.add_liq_data.coin_y = self.coin_y_combobox.get()
        self.add_liq_data.min_amount_out = float(self.min_amount_out_entry.get()) if not self.send_all_balance_checkbox.get() else 0
        self.add_liq_data.max_amount_out = float(self.max_amount_out_entry.get()) if not self.send_all_balance_checkbox.get() else 0
        self.add_liq_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.add_liq_data.gas_price = int(self.gas_price_entry.get())
        self.add_liq_data.gas_limit = int(self.gas_limit_entry.get())
        self.add_liq_data.min_delay_sec = float(self.min_delay_entry.get())
        self.add_liq_data.max_delay_sec = float(self.min_delay_entry.get())
        self.add_liq_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.add_liq_data.txn_wait_timeout_sec = int(self.transaction_wait_time_entry.get() if self.add_liq_data.wait_for_receipt else 0)
        self.add_liq_data.test_mode = self.test_mode_checkbox.get()

        return self.add_liq_data

    def save_config_event(self):
        if self.add_liq_switch.get() is True:
            pre_build_status = self.check_add_liq_config()
            if pre_build_status is not True:
                return
            config = self.get_add_liq_values()
        else:
            pre_build_status = self.check_remove_liq_config()
            if pre_build_status is not True:
                return
            config = self.get_remove_liq_values()

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
        if not self.add_liq_switch.get() and not self.remove_liq_switch.get():
            messagebox.showerror("Error", "Please select mode <Add Liquidity> or <Remove Liquidity>")
            return

        if self.add_liq_switch.get() is True:
            config = self.build_add_liq_config()
            if config is None:
                return

        else:
            config = self.build_remove_liq_config()
            if config is None:
                return

            if self.verify_wallets_amount() is False:
                return

        yesno = messagebox.askyesno("Warning", f"Are you sure you want to start"
                                               f" <{config.module_name.upper()}> module?\n\n"
                                               "Check all params carefully, if ready smash YES.")

        if yesno is False:
            return

        module_executor = ModuleExecutor(config)
        module_executor.start()

    def add_all_fields(self):
        self._add_liquidity_protocol_fields()
        self.add_add_liq_switch()
        self._add_coin_x_fields()
        self._add_coin_y_fields()
        self._add_min_amount_out_entry()
        self._add_max_amount_out_entry()
        self._add_send_all_balance_checkbox()
        self._add_common_settings_label_fields()
        self._add_gas_price_entry()
        self._add_gas_limit_entry()
        self._add_min_delay_entry()
        self._add_max_delay_entry()
        self._add_transaction_wait_time_entry()
        self._add_wait_for_transaction_checkbox()
        self._add_remove_liq_switch()
        self._add_coin_x2_fields()
        self._add_coin_y2_fields()
        self._add_test_mode_checkbox()
        self._add_next_button()




