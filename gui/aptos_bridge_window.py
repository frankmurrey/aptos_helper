import yaml

import customtkinter
from tkinter import (messagebox,
                     StringVar,
                     filedialog)

from gui.txn_settings_frame import TxnSettingsFrameBlueprint

from src.schemas.aptos_bridge import (ClaimConfigSchema,
                                      AptosBridgeConfigSchema)
from src.route_manager import (AptosBridgeRouteValidator,
                               AptosBridgeClaimConfigValidator)
from src.storage import Storage

from contracts.chains import Chains

from modules.module_executor import ModuleExecutor


class AptosBridgeModule(customtkinter.CTk):
    bridge_config: AptosBridgeConfigSchema
    claim_config: ClaimConfigSchema

    def __init__(self, tabview):
        super().__init__()

        self.tabview = tabview
        self._tab_name = "Aptos Bridge"
        self.txn_settings_frame = TxnSettingsFrameBlueprint(self.tabview.tab(self._tab_name),
                                                            is_common_fields_mark_need=True)
        self.txn_settings_frame.frame.grid(row=2, column=0, padx=(10, 0), pady=(20, 0), sticky="nsew")

        self.bridge_data = AptosBridgeConfigSchema()
        self.claim_data = ClaimConfigSchema()
        self.wallets_storage = Storage()

        self.claim_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                    text="+",
                                                    width=20,
                                                    height=20,
                                                    command=self.claim_event)

        self.bridge_settings_frame = customtkinter.CTkFrame(self.tabview.tab(self._tab_name))
        self.bridge_settings_frame.grid(row=1, column=0, padx=(10, 0), pady=(20, 0), sticky="nsew")

        self.dst_chain_combobox = customtkinter.CTkComboBox(self.bridge_settings_frame,
                                                            values=self._dst_chain_options,
                                                            command=self.update_coin_options)
        self.dst_coin_combobox = customtkinter.CTkComboBox(self.bridge_settings_frame,
                                                           values=self._dst_coin_options)

        self.min_amount_out_entry = customtkinter.CTkEntry(self.bridge_settings_frame,
                                                           width=140,
                                                           placeholder_text="10")

        self.max_amount_out_entry = customtkinter.CTkEntry(self.bridge_settings_frame,
                                                           width=140,
                                                           placeholder_text="20")

        self.send_all_balance_checkbox = customtkinter.CTkCheckBox(self.bridge_settings_frame,
                                                                   text="Send all balance",
                                                                   checkbox_width=18,
                                                                   checkbox_height=18,
                                                                   onvalue=True,
                                                                   offvalue=False,
                                                                   command=self.send_all_balance_checkbox_event)

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

    def _add_claim_button(self):
        claim_button_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                    text="Claim tokens",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_label.grid(row=0, column=0, padx=(45, 0), pady=(15, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=0, column=0, padx=(132, 0), pady=(15, 0), sticky="w")
        self.claim_button.grid(row=0, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_dst_chain_combobox(self):
        dst_chain_label = customtkinter.CTkLabel(self.bridge_settings_frame,
                                                 text="Destination Chain:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        dst_chain_label.grid(row=1, column=0, padx=(20, 0), pady=(10, 0), sticky="w")
        self.dst_chain_combobox.grid(row=2, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_dst_coin_combobox(self):
        dst_coin_label = customtkinter.CTkLabel(self.bridge_settings_frame,
                                                text="Coin to bridge:",
                                                font=customtkinter.CTkFont(size=12, weight="bold"))
        dst_coin_label.grid(row=1, column=1, padx=(45, 0), pady=(10, 0), sticky="w")
        self.dst_coin_combobox.grid(row=2, column=1, padx=(45, 0), pady=(0, 0), sticky="e")

    def _add_min_amount_out_entry(self):
        min_amount_out_label = customtkinter.CTkLabel(self.bridge_settings_frame,
                                                      text="Min amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_amount_out_entry.grid(row=4, column=0, padx=(20, 0), pady=(0, 15), sticky="w")

    def _add_max_amount_out_entry(self):
        max_amount_out_label = customtkinter.CTkLabel(self.bridge_settings_frame,
                                                      text="Max amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        max_amount_out_label.grid(row=3, column=1, padx=(45, 0), pady=(0, 0), sticky="w")
        self.max_amount_out_entry.grid(row=4, column=1, padx=(20, 0), pady=(0, 15), sticky="e")

    def _add_send_all_balance_checkbox(self):
        self.send_all_balance_checkbox.grid(row=5, column=0, padx=(20, 0), pady=(0, 15), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=13, column=0, padx=(20, 0), pady=(200, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=14, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_save_config_button(self):
        self.save_config_button.grid(row=14, column=0, padx=(210, 0), pady=(15, 0), sticky="w")

    def _add_load_config_button(self):
        self.load_config_button.grid(row=14, column=0, padx=(290, 0), pady=(15, 0), sticky="w")

    @property
    def _dst_chain_options(self):
        all_chains = Chains().all_chains
        return [chain.name for chain in all_chains]

    @property
    def _dst_coin_options(self):
        current_chain_option = self.dst_chain_combobox.get()
        current_chain_obj = Chains().get_by_name(current_chain_option)
        return current_chain_obj.supported_tokens

    def send_all_balance_checkbox_event(self):
        checkbox_status = self.send_all_balance_checkbox.get()
        if checkbox_status is True:
            self.min_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""),
                                                fg_color='#3f3f3f')
            self.max_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""),
                                                fg_color='#3f3f3f')
            self.min_amount_out_entry.configure(state="disabled")
            self.max_amount_out_entry.configure(state="disabled")
        else:
            self.min_amount_out_entry.configure(state="normal", placeholder_text="10", fg_color='#343638')
            self.max_amount_out_entry.configure(state="normal", placeholder_text="20", fg_color='#343638')

    def wait_for_transaction_checkbox_event(self):
        checkbox_status = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        if checkbox_status is True:
            self.txn_settings_frame.transaction_wait_time_entry.configure(state="normal",
                                                                          placeholder_text="120",
                                                                          fg_color='#343638')
        else:
            self.txn_settings_frame.transaction_wait_time_entry.configure(placeholder_text="",
                                                                          textvariable=StringVar(value=""),
                                                                          fg_color='#3f3f3f')
            self.txn_settings_frame.transaction_wait_time_entry.configure(state="disabled")

    def update_coin_options(self, chain_value):
        current_chain_obj = Chains().get_by_name(chain_value)
        self.dst_coin_combobox.configure(values=current_chain_obj.supported_tokens)
        self.dst_coin_combobox.set(current_chain_obj.supported_tokens[0])
    
    def update_all_fields(self):
        self.dst_coin_combobox.set(self.bridge_data.coin_to_bridge)
        self.dst_chain_combobox.set(self.bridge_data.dst_chain_name)

        if self.bridge_data.send_all_balance is True:
            self.send_all_balance_checkbox.select()
            self.min_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""),
                                                fg_color="#3f3f3f")
            self.max_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""),
                                                fg_color="#3f3f3f")
            self.min_amount_out_entry.configure(state="disabled")
            self.max_amount_out_entry.configure(state="disabled")
        else:
            self.send_all_balance_checkbox.deselect()
            self.min_amount_out_entry.configure(state="normal",
                                                textvariable=StringVar(value=self.bridge_data.min_amount_out),
                                                fg_color="#343638")
            self.max_amount_out_entry.configure(state="normal",
                                                textvariable=StringVar(value=self.bridge_data.max_amount_out),
                                                fg_color="#343638")

        self.txn_settings_frame.gas_price_entry.configure(textvariable=StringVar(value=self.bridge_data.gas_price))
        self.txn_settings_frame.gas_limit_entry.configure(textvariable=StringVar(value=self.bridge_data.gas_limit))
        if self.bridge_data.force_gas_limit is True:
            self.txn_settings_frame.force_gas_limit_checkbox.select()
        else:
            self.txn_settings_frame.force_gas_limit_checkbox.deselect()

        self.txn_settings_frame.min_delay_entry.configure(textvariable=StringVar(value=self.bridge_data.min_delay_sec))
        self.txn_settings_frame.max_delay_entry.configure(textvariable=StringVar(value=self.bridge_data.max_delay_sec))

        if self.bridge_data.wait_for_receipt is True:
            self.txn_settings_frame.wait_for_transaction_checkbox.select()
            self.txn_settings_frame.transaction_wait_time_entry.configure(
                textvariable=StringVar(value=self.bridge_data.txn_wait_timeout_sec),
                fg_color="#343638")
        else:
            self.txn_settings_frame.wait_for_transaction_checkbox.deselect()
            self.txn_settings_frame.transaction_wait_time_entry.configure(placeholder_text="",
                                                                          fg_color="#3f3f3f")
            self.txn_settings_frame.transaction_wait_time_entry.configure(state="disabled")
        if self.bridge_data.test_mode is True:
            self.test_mode_checkbox.select()
        else:
            self.test_mode_checkbox.deselect()

    def get_claim_data_values(self):
        self.claim_data.gas_limit = self.txn_settings_frame.gas_limit_entry.get()
        self.claim_data.gas_price = self.txn_settings_frame.gas_price_entry.get()
        self.claim_data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.claim_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.claim_data.txn_wait_timeout_sec = self.txn_settings_frame.transaction_wait_time_entry.get()
        self.claim_data.test_mode = self.test_mode_checkbox.get()
        self.claim_data.min_delay_sec = self.txn_settings_frame.min_delay_entry.get()
        self.claim_data.max_delay_sec = self.txn_settings_frame.max_delay_entry.get()

        return self.claim_data

    def check_claim_config(self):
        route_validator = AptosBridgeClaimConfigValidator(self.get_claim_data_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_claim_config(self):
        pre_build_status = self.check_claim_config()
        if pre_build_status is not True:
            return

        self.claim_data.gas_limit = int(self.txn_settings_frame.gas_price_entry.get() if self.txn_settings_frame.gas_price_entry.get().strip(" ") != "" else "")
        self.claim_data.gas_price = float(self.txn_settings_frame.gas_price_entry.get() if self.txn_settings_frame.gas_price_entry.get()(" ") != "" else "")
        self.claim_data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.claim_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.claim_data.txn_wait_timeout_sec = float(self.txn_settings_frame.transaction_wait_time_entry.get() if self.txn_settings_frame.transaction_wait_time_entry.get() else 0)
        self.claim_data.test_mode = self.test_mode_checkbox.get()
        self.claim_data.min_delay_sec = float(self.txn_settings_frame.min_delay_entry.get() if self.txn_settings_frame.min_delay_entry.get().strip(" ") != "" else "")
        self.claim_data.max_delay_sec = float(self.txn_settings_frame.max_delay_entry.get() if self.txn_settings_frame.max_delay_entry.get().strip(" ") != "" else "")

        return self.claim_data

    def get_bridge_data_values(self):
        self.bridge_data.coin_to_bridge = self.dst_coin_combobox.get()
        self.bridge_data.dst_chain_name = self.dst_chain_combobox.get()
        self.bridge_data.min_amount_out = self.min_amount_out_entry.get()
        self.bridge_data.max_amount_out = self.max_amount_out_entry.get()
        self.bridge_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.bridge_data.gas_price = self.txn_settings_frame.gas_price_entry.get()
        self.bridge_data.gas_limit = self.txn_settings_frame.gas_limit_entry.get()
        self.bridge_data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.bridge_data.min_delay_sec = self.txn_settings_frame.min_delay_entry.get()
        self.bridge_data.max_delay_sec = self.txn_settings_frame.max_delay_entry.get()
        self.bridge_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.bridge_data.txn_wait_timeout_sec = self.txn_settings_frame.transaction_wait_time_entry.get()
        self.bridge_data.test_mode = self.test_mode_checkbox.get()

        return self.bridge_data

    def check_bridge_config(self):
        route_validator = AptosBridgeRouteValidator(self.get_bridge_data_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_bridge_config(self):
        pre_build_status = self.check_bridge_config()
        if pre_build_status is not True:
            return

        self.bridge_data.coin_to_bridge = self.dst_coin_combobox.get()
        self.bridge_data.dst_chain_name = self.dst_chain_combobox.get()
        self.bridge_data.min_amount_out = float(self.min_amount_out_entry.get()) if self.bridge_data.min_amount_out.strip(" ") != "" else ""
        self.bridge_data.max_amount_out = float(self.max_amount_out_entry.get()) if self.bridge_data.max_amount_out.strip(" ") != "" else ""
        self.bridge_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.bridge_data.gas_price = float(self.txn_settings_frame.gas_price_entry.get() if self.bridge_data.gas_price.strip(" ") != "" else "")
        self.bridge_data.gas_limit = int(self.txn_settings_frame.gas_limit_entry.get() if self.bridge_data.gas_limit.strip(" ") != "" else "")
        self.bridge_data.force_gas_limit = self.txn_settings_frame.force_gas_limit_checkbox.get()
        self.bridge_data.min_delay_sec = float(self.txn_settings_frame.min_delay_entry.get() if self.bridge_data.min_delay_sec.strip(" ") != "" else "")
        self.bridge_data.max_delay_sec = float(self.txn_settings_frame.max_delay_entry.get() if self.bridge_data.max_delay_sec.strip(" ") != "" else "")
        self.bridge_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.bridge_data.txn_wait_timeout_sec = int(self.txn_settings_frame.transaction_wait_time_entry.get() if self.bridge_data.wait_for_receipt else 0)
        self.bridge_data.test_mode = self.test_mode_checkbox.get()

        return self.bridge_data

    def save_config_event(self):
        pre_build_status = self.check_bridge_config()
        if pre_build_status is not True:
            return
        config = self.get_bridge_data_values()

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
            config = AptosBridgeConfigSchema(**config_dict)
            if config.module_name != "aptos_bridge":
                messagebox.showerror("Error", f"Wrong config file selected, current module is <aptos_bridge>,"
                                              f" selected module is <{config.module_name}>")
                return

            self.bridge_data = config
            self.update_all_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Wrong config file selected, error: {e}")

    def claim_event(self):
        config = self.build_claim_config()
        if config is None:
            return

        if self.verify_wallets_amount(is_claim=True) is False:
            return

        yesno = messagebox.askyesno("Warning", "Are you sure you want to start claim?\n"
                                               "Check all params carefully, if ready smash YES.")

        if yesno is False:
            return

        module_executor = ModuleExecutor(config)
        module_executor.start()

    def verify_wallets_amount(self, is_claim=False):
        wallets_data = self.wallets_storage.get_wallets_data()
        if not wallets_data:
            messagebox.showerror("Error", "No wallets provided")
            return False

        aptos_wallets = [wallet.wallet for wallet in wallets_data if wallet.wallet is not None]
        evm_addresses = [wallet.evm_pair_address for wallet in wallets_data if wallet.evm_pair_address is not None]

        if len(aptos_wallets) == 0:
            messagebox.showerror("Error", "No aptos wallets provided")
            return False

        if is_claim is False:
            if len(evm_addresses) == 0:
                messagebox.showerror("Error", "No evm addresses provided")
                return False

            if len(aptos_wallets) != len(evm_addresses):
                messagebox.showerror("Error", "Aptos wallets and evm addresses amount must be equal")
                return False

        return True

    def next_button_event(self):
        config = self.build_bridge_config()
        if config is None:
            return

        if self.verify_wallets_amount() is False:
            return

        yesno = messagebox.askyesno("Warning", "Are you sure you want to start?\n"
                                               "Check all params carefully, if ready smash YES.")

        if yesno is False:
            return

        module_executor = ModuleExecutor(config)
        module_executor.start()

    def add_all_fields(self):
        self._add_dst_chain_combobox()
        self._add_dst_coin_combobox()
        self._add_min_amount_out_entry()
        self._add_max_amount_out_entry()
        self._add_send_all_balance_checkbox()
        self._add_test_mode_checkbox()
        self._add_claim_button()
        self._add_next_button()
        self._add_save_config_button()
        self._add_load_config_button()
