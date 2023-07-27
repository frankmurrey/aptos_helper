import yaml

import customtkinter
from tkinter import (messagebox,
                     StringVar,
                     filedialog)

from src.schemas.able_finance import (AbleMintConfigSchema,
                                      AbleRedeemConfigSchema)

from contracts.tokens import Tokens

from src.route_manager import (AbleFinanceMintConfigValidator,
                               AbleFinanceRedeemConfigValidator)
from src.storage import WalletsStorage

from modules.module_executor import ModuleExecutor


class AbleFinanceWindow(customtkinter.CTk):
    mint_data: AbleMintConfigSchema
    redeem_data: AbleRedeemConfigSchema

    def __init__(self, tabview):
        super().__init__()

        self.tabview = tabview
        self._tab_name = "Abel finance"

        self.mint_data = AbleMintConfigSchema()
        self.redeem_data = AbleRedeemConfigSchema()
        self.wallets_storage = WalletsStorage()

        self.claim_button = customtkinter.CTkButton(self.tabview.tab(self._tab_name),
                                                    text="-",
                                                    width=20,
                                                    height=20,
                                                    command=self.redeem_button_event)

        self.coin_option_combobox = customtkinter.CTkComboBox(self.tabview.tab(self._tab_name),
                                                              values=self._available_coins)

        self.min_amount_out_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                           width=140,
                                                           placeholder_text="10")
        self.max_amount_out_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                           width=140,
                                                           placeholder_text="20")

        self.send_all_balance_checkbox = customtkinter.CTkCheckBox(self.tabview.tab(self._tab_name),
                                                                   text="Send all balance",
                                                                   checkbox_width=18,
                                                                   checkbox_height=18,
                                                                   onvalue=True,
                                                                   offvalue=False,
                                                                   command=self.send_all_balance_checkbox_event)

        self.gas_price_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=70)

        self.gas_limit_entry = customtkinter.CTkEntry(self.tabview.tab(self._tab_name),
                                                      width=70)

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

    @property
    def _available_coins(self):
        tokens = Tokens().get_abel_finance_available_coins()
        return [token.symbol.upper() for token in tokens]

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

    def _add_claim_button(self):
        claim_button_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                    text="Unstake chosen coin",
                                                    font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_label.grid(row=0, column=0, padx=(45, 0), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=0, column=0, padx=(180, 0), pady=(0, 0), sticky="w")
        self.claim_button.grid(row=0, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_coin_option_combobox_fields(self):
        coin_option_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="Select coin:",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        coin_option_label.grid(row=1, column=0, sticky="w", padx=(20, 0), pady=(0, 0))
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=1, column=0, padx=(96, 0), pady=(0, 0), sticky="w")
        self.coin_option_combobox.grid(row=2, column=0, sticky="w", padx=(20, 0), pady=(0, 0))

    def _add_min_amount_out_entry(self):
        min_amount_out_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                      text="Min amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        min_amount_out_label.grid(row=3, column=0, sticky="w", padx=(20, 0), pady=(0, 0))
        self.min_amount_out_entry.grid(row=4, column=0, sticky="w", padx=(20, 0), pady=(0, 0))

    def _add_max_amount_out_entry(self):
        max_amount_out_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                      text="Max amount out:",
                                                      font=customtkinter.CTkFont(size=12, weight="bold"))
        max_amount_out_label.grid(row=3, column=1, sticky="w", padx=(0, 0), pady=(0, 0))
        self.max_amount_out_entry.grid(row=4, column=1, sticky="e", padx=(0, 20), pady=(0, 0))

    def _add_send_all_balance_checkbox(self):
        self.send_all_balance_checkbox.grid(row=5, column=0, padx=(20, 0), pady=(5, 0), sticky="w")

    def _add_gas_price_entry(self):
        gas_price_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Gas price:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        gas_price_label.grid(row=6, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=6, column=0, padx=(85, 0), pady=(0, 0), sticky="w")
        self.gas_price_entry.grid(row=7, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_gas_limit_entry(self):
        gas_limit_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Gas limit:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        gas_limit_label.grid(row=6, column=0, padx=(105, 0), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=6, column=0, padx=(168, 0), pady=(0, 0), sticky="w")
        self.gas_limit_entry.grid(row=7, column=0, padx=(105, 0), pady=(0, 0), sticky="w")

    def _add_min_delay_entry(self):
        min_delay_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Min delay:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        min_delay_label.grid(row=8, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=8, column=0, padx=(87, 0), pady=(0, 0), sticky="w")
        self.min_delay_entry.grid(row=9, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_max_delay_entry(self):
        max_delay_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                 text="Max delay:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))
        max_delay_label.grid(row=8, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="yellow",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=8, column=1, padx=(70, 0), pady=(0, 0), sticky="w")
        self.max_delay_entry.grid(row=9, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_transaction_wait_time_entry(self):
        transaction_wait_time_label = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                             text="Transaction wait time (sec):",
                                                             font=customtkinter.CTkFont(size=12, weight="bold"))

        transaction_wait_time_label.grid(row=10, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        claim_button_mark = customtkinter.CTkLabel(self.tabview.tab(self._tab_name),
                                                   text="*",
                                                   text_color="#ADD8E6",
                                                   font=customtkinter.CTkFont(size=12, weight="bold"))
        claim_button_mark.grid(row=10, column=0, padx=(200, 0), pady=(0, 0), sticky="w")
        self.transaction_wait_time_entry.grid(row=11, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_wait_for_transaction_checkbox(self):
        self.wait_for_transaction_checkbox.grid(row=12, column=0, padx=(20, 0), pady=(5, 0), sticky="w")

    def _add_test_mode_checkbox(self):
        self.test_mode_checkbox.grid(row=13, column=0, padx=(20, 0), pady=(250, 0), sticky="w")

    def _add_next_button(self):
        self.next_button.grid(row=14, column=0, padx=(20, 0), pady=(15, 0), sticky="w")

    def _add_save_config_button(self):
        self.save_config_button.grid(row=14, column=1, padx=(0, 0), pady=(15, 0), sticky="w")

    def _add_load_config_button(self):
        self.load_config_button.grid(row=14, column=1, padx=(80, 0), pady=(15, 0), sticky="w")

    def update_all_fields(self):
        self.coin_option_combobox.set(self.mint_data.coin_option)

        if self.mint_data.send_all_balance is True:
            self.send_all_balance_checkbox.select()
            self.min_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""))
            self.max_amount_out_entry.configure(placeholder_text="",
                                                textvariable=StringVar(value=""))
            self.min_amount_out_entry.configure(state="disabled")
            self.max_amount_out_entry.configure(state="disabled")
        else:
            self.send_all_balance_checkbox.deselect()
            self.min_amount_out_entry.configure(state="normal",
                                                textvariable=StringVar(value=self.mint_data.min_amount_out))
            self.max_amount_out_entry.configure(state="normal",
                                                textvariable=StringVar(value=self.mint_data.max_amount_out))

        self.gas_price_entry.configure(textvariable=StringVar(value=self.mint_data.gas_price))
        self.gas_limit_entry.configure(textvariable=StringVar(value=self.mint_data.gas_limit))

        self.min_delay_entry.configure(textvariable=StringVar(value=self.mint_data.min_delay_sec))
        self.max_delay_entry.configure(textvariable=StringVar(value=self.mint_data.max_delay_sec))

        if self.mint_data.wait_for_receipt is True:
            self.wait_for_transaction_checkbox.select()
            self.transaction_wait_time_entry.configure(textvariable=StringVar(value=self.mint_data.txn_wait_timeout_sec))
        else:
            self.wait_for_transaction_checkbox.deselect()
            self.transaction_wait_time_entry.configure(placeholder_text="")
            self.transaction_wait_time_entry.configure(state="disabled")
        if self.mint_data.test_mode is True:
            self.test_mode_checkbox.select()
        else:
            self.test_mode_checkbox.deselect()

    def get_redeem_data_values(self):
        self.redeem_data.coin_option = self.coin_option_combobox.get()
        self.redeem_data.redeem_all = True
        self.redeem_data.gas_price = self.gas_price_entry.get()
        self.redeem_data.gas_limit = self.gas_limit_entry.get()
        self.redeem_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.mint_data.txn_wait_timeout_sec = self.transaction_wait_time_entry.get()
        self.mint_data.test_mode = self.test_mode_checkbox.get()

        return self.redeem_data

    def check_redeem_config(self):
        route_validator = AbleFinanceRedeemConfigValidator(self.get_mint_data_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_redeem_config(self):
        pre_build_status = self.check_redeem_config()
        if pre_build_status is not True:
            return

        self.redeem_data.coin_option = self.coin_option_combobox.get()
        self.redeem_data.redeem_all = True
        self.redeem_data.gas_price = int(self.gas_price_entry.get())
        self.redeem_data.gas_limit = int(self.gas_limit_entry.get())
        self.redeem_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.redeem_data.txn_wait_timeout_sec = int(self.transaction_wait_time_entry.get() if self.mint_data.wait_for_receipt else 0)
        self.redeem_data.test_mode = self.test_mode_checkbox.get()

        return self.redeem_data

    def get_mint_data_values(self):
        self.mint_data.coin_option = self.coin_option_combobox.get()
        self.mint_data.min_amount_out = self.min_amount_out_entry.get()
        self.mint_data.max_amount_out = self.max_amount_out_entry.get()
        self.mint_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.mint_data.gas_price = self.gas_price_entry.get()
        self.mint_data.gas_limit = self.gas_limit_entry.get()
        self.mint_data.min_delay_sec = self.min_delay_entry.get()
        self.mint_data.max_delay_sec = self.max_delay_entry.get()
        self.mint_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.mint_data.txn_wait_timeout_sec = self.transaction_wait_time_entry.get()
        self.mint_data.test_mode = self.test_mode_checkbox.get()

        return self.mint_data

    def check_mint_config(self):
        route_validator = AbleFinanceMintConfigValidator(self.get_mint_data_values())
        validation_status = route_validator.check_is_route_valid()
        if validation_status is not True:
            messagebox.showerror("Error", validation_status)
            return

        return True

    def build_mint_config(self):
        pre_build_status = self.check_mint_config()
        if pre_build_status is not True:
            return

        self.mint_data.coin_option = self.coin_option_combobox.get()
        self.mint_data.min_amount_out = float(self.min_amount_out_entry.get() if not self.mint_data.send_all_balance else 0)
        self.mint_data.max_amount_out = float(self.max_amount_out_entry.get() if not self.mint_data.send_all_balance else 0)
        self.mint_data.send_all_balance = self.send_all_balance_checkbox.get()
        self.mint_data.gas_price = int(self.gas_price_entry.get())
        self.mint_data.gas_limit = int(self.gas_limit_entry.get())
        self.mint_data.min_delay_sec = float(self.min_delay_entry.get())
        self.mint_data.max_delay_sec = float(self.max_delay_entry.get())
        self.mint_data.wait_for_receipt = self.wait_for_transaction_checkbox.get()
        self.mint_data.txn_wait_timeout_sec = int(self.transaction_wait_time_entry.get() if self.mint_data.wait_for_receipt else 0)
        self.mint_data.test_mode = self.test_mode_checkbox.get()

        return self.mint_data

    def save_config_event(self):
        pre_build_status = self.check_mint_config()
        if pre_build_status is not True:
            return
        config = self.get_mint_data_values()

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
            config = AbleMintConfigSchema(**config_dict)
            if config.module_name != "able_mint":
                messagebox.showerror("Error", f"Wrong config file selected, current module is <able_mint>,"
                                              f" selected module is <{config.module_name}>")
                return

            self.mint_data = config
            self.update_all_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Wrong config file selected, error: {e}")

    def redeem_button_event(self):
        config = self.build_redeem_config()
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
        config = self.build_mint_config()
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
        self._add_claim_button()
        self._add_coin_option_combobox_fields()
        self._add_min_amount_out_entry()
        self._add_max_amount_out_entry()
        self._add_send_all_balance_checkbox()
        self._add_gas_price_entry()
        self._add_gas_limit_entry()
        self._add_min_delay_entry()
        self._add_max_delay_entry()
        self._add_transaction_wait_time_entry()
        self._add_wait_for_transaction_checkbox()
        self._add_test_mode_checkbox()
        self._add_next_button()
        self._add_save_config_button()
        self._add_load_config_button()



