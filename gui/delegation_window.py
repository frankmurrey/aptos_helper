import yaml

import customtkinter
from tkinter import (messagebox,
                     StringVar,
                     filedialog
)

from gui.txn_settings_frame import TxnSettingsFrameBlueprint

from src.schemas.delegation import (DelegateConfigSchema,
                                    UnlockConfigSchema)
from src.route_manager import (DelegationConfigValidator)
from src.storage import Storage


from modules.module_executor import ModuleExecutor


class DelegationWindow(customtkinter.CTk):
    delegate_config: DelegateConfigSchema
    unlock_config: UnlockConfigSchema

    def __init__(self, tabview):
        super().__init__()
        self.tabview = tabview
        self._tab_name = "Delegate"
        self.txn_settings_frame = TxnSettingsFrameBlueprint(self.tabview.tab(self._tab_name))
        self.txn_settings_frame.frame.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.delegate_data = DelegateConfigSchema()
        self.unlock_data = UnlockConfigSchema()

        self.validator_address = None

        self.wallets_storage = Storage()

        self.unlock_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                     text="+",
                                                     width=20,
                                                     height=20,
                                                     command=self.unlock_button_event)

        self.delegate_settings_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                              text="Delegate Aptos:",
                                                              text_color="#6fc276",
                                                              font=customtkinter.CTkFont(size=16, weight="bold"))
        self.delegate_settings_label.grid(row=1, column=0, padx=20, pady=(15, 0), sticky="w")

        self.delegate_settings_frame = customtkinter.CTkFrame(self.tabview.tab(self._tab_name))
        self.delegate_settings_frame.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="nsew")

        self.min_amount_out_entry = customtkinter.CTkEntry(self.delegate_settings_frame,
                                                           textvariable=StringVar(value="11"),
                                                           width=140,)

        self.max_amount_out_entry = customtkinter.CTkEntry(self.delegate_settings_frame,
                                                           width=140)

        self.validator_address_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                              text="Validator address:",
                                                              font=customtkinter.CTkFont(size=16, weight="bold"),
                                                              text_color="#99CCFF")
        self.validator_address_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")

        self.validator_address_frame = customtkinter.CTkFrame(self.tabview.tab(self._tab_name))
        self.validator_address_frame.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="nsew")

        self.validator_address_input_button = customtkinter.CTkButton(self.validator_address_frame,
                                                                      text="+",
                                                                      width=20,
                                                                      height=20,
                                                                      command=self.input_validator_address_button_event)
        self.validator_address_displayer_label = customtkinter.CTkLabel(self.validator_address_frame,
                                                                        text="Not imported",
                                                                        text_color='gray',
                                                                        font=customtkinter.CTkFont(size=12,
                                                                                                   weight="bold"))

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
                                                          width=70,
                                                          command=self.load_config_event)

    def _add_unlock_button_fields(self):
        unlock_button_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                     text="Unlock staked",
                                                     font=customtkinter.CTkFont(size=12, weight="bold"))
        unlock_button_label.grid(row=0, column=0, padx=45, pady=(15, 0), sticky="w")
        unlock_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                    text="*",
                                                    text_color="yellow",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))
        unlock_button_mark.grid(row=0, column=0, padx=(137, 0), pady=(0, 0), sticky="w")
        self.unlock_button.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")

    def _add_min_amount_out_fields(self):
        min_amount_out_label = customtkinter.CTkLabel(self.delegate_settings_frame,
                                                      text="Min amount out",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=1, column=0, padx=(20, 0), pady=(10, 0), sticky="w")
        self.min_amount_out_entry.grid(row=2, column=0, padx=(20, 0), pady=(0, 20), sticky="w")

    def _add_max_amount_out_fields(self):
        max_amount_out_label = customtkinter.CTkLabel(self.delegate_settings_frame,
                                                      text="Max amount out",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        max_amount_out_label.grid(row=1, column=1, padx=(20, 0), pady=(10, 0), sticky="w")
        self.max_amount_out_entry.grid(row=2, column=1, padx=(20, 0), pady=(0, 20), sticky="w")

    def _add_validator_address_fields(self):
        validator_address_label = customtkinter.CTkLabel(self.validator_address_frame,
                                                         text="Input validator address",
                                                         font=customtkinter.CTkFont(size=12, weight="bold"))
        validator_address_label.grid(row=1, column=0, padx=50, pady=(15, 0), sticky="w")
        unlock_button_mark = customtkinter.CTkLabel(self.validator_address_frame,
                                                    text="*",
                                                    text_color="yellow",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))
        unlock_button_mark.grid(row=1, column=0, padx=(200, 0), pady=(0, 0), sticky="w")
        self.validator_address_input_button.grid(row=1, column=0, padx=20, pady=(15, 0), sticky="w")

    def _add_validator_address_displayer_label(self):
        self.validator_address_displayer_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=6, column=0, padx=(20, 0), pady=(120, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=7, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_save_config_button(self):
        self.save_config_button.grid(row=7, column=0, padx=(210, 0), pady=(15, 0), sticky="w")

    def _add_load_config_button(self):
        self.load_config_button.grid(row=7, column=0, padx=(290, 0), pady=(15, 0), sticky="w")

    def input_validator_address_button_event(self):
        dialog = customtkinter.CTkInputDialog(text="Input validator address:", title="Input")
        raw_addr = dialog.get_input()
        if not raw_addr:
            self.validator_address = None
            return

        if len(raw_addr) != 66:
            messagebox.showerror("Error", "Address should be 66 symbols len")
            self.validator_address = None
        else:
            self.validator_address = raw_addr
        self.update_address_displayer()

    def get_validator_address_for_displayer(self):
        current_address = self.validator_address
        if current_address is None:
            return f"Incorrect format, try again"

        if len(current_address) == 66:
            short_address = f"{current_address[:12]}...{current_address[-12:]}"
        else:
            short_address = f"Incorrect format, try again"

        return short_address

    def update_address_displayer(self):
        short_address = self.get_validator_address_for_displayer()
        if self.validator_address:
            self.validator_address_displayer_label.configure(text=short_address,
                                                             text_color="#6fc276")
        else:
            self.validator_address_displayer_label.configure(text=short_address,
                                                             text_color="#F47174")

    def get_unlock_values(self):
        self.unlock_data.validator_addr = self.validator_address
        self.unlock_data.gas_price = self.txn_settings_frame.gas_price_entry.get()
        self.unlock_data.gas_limit = self.txn_settings_frame.gas_limit_entry.get()
        self.unlock_data.min_delay_sec = self.txn_settings_frame.min_delay_entry.get()
        self.unlock_data.max_delay_sec = self.txn_settings_frame.max_delay_entry.get()
        self.unlock_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.unlock_data.txn_wait_timeout_sec = self.txn_settings_frame.transaction_wait_time_entry.get()
        self.unlock_data.test_mode = self.test_mode_checkbox.get()
        self.unlock_data.min_amount_out = 1
        self.unlock_data.max_amount_out = 1

        return self.unlock_data

    def check_unlock_config(self):
        route_validator = DelegationConfigValidator(self.get_unlock_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return False

        return True

    def build_unlock_config(self):
        pre_build_status = self.check_unlock_config()
        if pre_build_status is not True:
            return

        self.unlock_data.validator_addr = self.validator_address
        self.unlock_data.gas_price = float(self.txn_settings_frame.gas_price_entry.get()) if self.txn_settings_frame.gas_price_entry.get().strip(
            " ") != "" else ""
        self.unlock_data.gas_limit = int(self.txn_settings_frame.gas_limit_entry.get()) if self.txn_settings_frame.gas_limit_entry.get().strip(
            " ") != "" else ""
        self.unlock_data.min_delay_sec = int(self.txn_settings_frame.min_delay_entry.get()) if self.txn_settings_frame.min_delay_entry.get().strip(
            " ") != "" else ""
        self.unlock_data.max_delay_sec = int(self.txn_settings_frame.max_delay_entry.get()) if self.txn_settings_frame.max_delay_entry.get().strip(
            " ") != "" else ""
        self.unlock_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.unlock_data.txn_wait_timeout_sec = int(
            self.txn_settings_frame.transaction_wait_time_entry.get()) if self.txn_settings_frame.wait_for_transaction_checkbox.get() else ""

        return self.unlock_data

    def get_delegate_values(self):
        self.delegate_data.validator_addr = self.validator_address
        self.delegate_data.gas_price = self.txn_settings_frame.gas_price_entry.get()
        self.delegate_data.gas_limit = self.txn_settings_frame.gas_limit_entry.get()
        self.delegate_data.min_delay_sec = self.txn_settings_frame.min_delay_entry.get()
        self.delegate_data.max_delay_sec = self.txn_settings_frame.max_delay_entry.get()
        self.delegate_data.min_amount_out = self.min_amount_out_entry.get()
        self.delegate_data.max_amount_out = self.max_amount_out_entry.get()
        self.delegate_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.delegate_data.txn_wait_timeout_sec = self.txn_settings_frame.transaction_wait_time_entry.get()
        self.delegate_data.test_mode = self.test_mode_checkbox.get()

        return self.delegate_data

    def check_delegate_config(self):
        route_validator = DelegationConfigValidator(self.get_delegate_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return False

        return True

    def build_delegate_config(self):
        pre_build_status = self.check_delegate_config()
        if pre_build_status is not True:
            return

        self.delegate_data.validator_addr = self.validator_address
        self.delegate_data.gas_price = int(self.txn_settings_frame.gas_price_entry.get()) if self.txn_settings_frame.gas_price_entry.get().strip(" ") != "" else ""
        self.delegate_data.gas_limit = int(self.txn_settings_frame.gas_limit_entry.get()) if self.txn_settings_frame.gas_limit_entry.get().strip(" ") != "" else ""
        self.delegate_data.min_delay_sec = int(self.txn_settings_frame.min_delay_entry.get()) if self.txn_settings_frame.min_delay_entry.get().strip(" ") != "" else ""
        self.delegate_data.max_delay_sec = int(self.txn_settings_frame.max_delay_entry.get()) if self.txn_settings_frame.max_delay_entry.get().strip(" ") != "" else ""
        self.delegate_data.min_amount_out = float(self.min_amount_out_entry.get()) if self.min_amount_out_entry.get().strip(" ") != "" else ""
        self.delegate_data.max_amount_out = float(self.max_amount_out_entry.get()) if self.max_amount_out_entry.get().strip(" ") != "" else ""
        self.delegate_data.wait_for_receipt = self.txn_settings_frame.wait_for_transaction_checkbox.get()
        self.delegate_data.txn_wait_timeout_sec = int(self.txn_settings_frame.transaction_wait_time_entry.get()) if self.txn_settings_frame.wait_for_transaction_checkbox.get() else ""

        return self.delegate_data

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

    def update_all_fields(self):
        self.min_amount_out_entry.configure(state="normal",
                                            textvariable=StringVar(value=self.delegate_data.min_amount_out))
        self.max_amount_out_entry.configure(state="normal",
                                            textvariable=StringVar(value=self.delegate_data.max_amount_out))
        self.validator_address = self.delegate_data.validator_addr
        self.update_address_displayer()

        self.txn_settings_frame.gas_price_entry.configure(textvariable=StringVar(value=self.delegate_data.gas_price))
        self.txn_settings_frame.gas_limit_entry.configure(textvariable=StringVar(value=self.delegate_data.gas_limit))

        self.txn_settings_frame.min_delay_entry.configure(textvariable=StringVar(value=self.delegate_data.min_delay_sec))
        self.txn_settings_frame.max_delay_entry.configure(textvariable=StringVar(value=self.delegate_data.max_delay_sec))

        if self.delegate_data.wait_for_receipt is True:
            self.txn_settings_frame.wait_for_transaction_checkbox.select()
            self.txn_settings_frame.transaction_wait_time_entry.configure(textvariable=StringVar(value=self.delegate_data.txn_wait_timeout_sec),
                                                       fg_color='#343638')
        else:
            self.txn_settings_frame.wait_for_transaction_checkbox.deselect()
            self.txn_settings_frame.transaction_wait_time_entry.configure(placeholder_text="")
            self.txn_settings_frame.transaction_wait_time_entry.configure(state="disabled",
                                                       fg_color='#3f3f3f')
        if self.delegate_data.test_mode is True:
            self.test_mode_checkbox.select()
        else:
            self.test_mode_checkbox.deselect()

    def save_config_event(self):
        pre_build_status = self.check_delegate_config()
        if pre_build_status is not True:
            return
        config = self.build_delegate_config()

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
            config = DelegateConfigSchema(**config_dict)
            if config.module_name != "delegate":
                messagebox.showerror("Error", f"Wrong config file selected, current module is <delegate>,"
                                              f" selected module is <{config.module_name}>")
                return

            self.delegate_data = config
            self.update_all_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Wrong config file selected, error: {e}")

    def unlock_button_event(self):
        config = self.build_unlock_config()
        if config is None:
            return

        if self.verify_wallets_amount() is False:
            return

        yesno = messagebox.askyesno("Warning", "Are you sure you want to start unlock?\n"
                                               "Check all params carefully, if ready smash YES.")

        if yesno is False:
            return

        module_executor = ModuleExecutor(config)
        module_executor.start()

    def next_button_event(self):
        config = self.build_delegate_config()
        if config is None:
            return

        if self.verify_wallets_amount() is False:
            return

        yesno = messagebox.askyesno("Warning", "Are you sure you want to start delegation?\n"
                                               "Check all params carefully, if ready smash YES.")

        if yesno is False:
            return

        module_executor = ModuleExecutor(config)
        module_executor.start()

    def add_all_fields(self):
        self._add_unlock_button_fields()
        self._add_min_amount_out_fields()
        self._add_max_amount_out_fields()
        self._add_validator_address_fields()
        self._add_validator_address_displayer_label()
        self._add_test_mode_checkbox()
        self._add_next_button()
        self._add_save_config_button()
        self._add_load_config_button()

