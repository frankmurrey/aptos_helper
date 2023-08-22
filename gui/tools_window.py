import customtkinter

from src.utils.generate_wallets import generate_keys

from src.schemas.balance_checker import BalanceCheckerConfigSchema
from src.schemas.app_config import AppConfigSchema
from src.paths import APP_CONFIG_FILE

from src.file_manager import FileManager

from modules.module_executor import ModuleExecutor

from contracts.tokens import Tokens
from contracts.base import Token

from tkinter import (messagebox,
                     filedialog,
                     StringVar
                     )

from src.storage import Storage

from src.utils.tokens_editor import TokensEditor


class ToolsTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage = Storage()

        self.tokens_editor = TokensEditor()
        self.token_contract_to_add = None

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

        self.app_config_label = customtkinter.CTkLabel(self,
                                                       text="App config:",
                                                       font=customtkinter.CTkFont(size=14, weight="bold"))
        self.app_config_label.grid(row=4, column=0, padx=15, pady=5, sticky="w")
        self.app_config_frame = customtkinter.CTkFrame(master=self)
        self.app_config_frame.grid(row=5, column=0, padx=15, sticky="nsew")

        self.preserve_logs_checkbox = customtkinter.CTkCheckBox(self.app_config_frame,
                                                                text="Preserve wallet actions logs",
                                                                checkbox_width=20,
                                                                checkbox_height=20,
                                                                onvalue=True,
                                                                offvalue=False)
        self.preserve_logs_checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.proxy_rotation_link_label = customtkinter.CTkLabel(self.app_config_frame,
                                                                text="Proxy rotation link:")
        self.proxy_rotation_link_label.grid(row=1, column=0, padx=10, pady=(0, 0), sticky="w")

        self.proxy_rotation_link_entry = customtkinter.CTkEntry(self.app_config_frame,
                                                                width=280,
                                                                state="disabled",
                                                                fg_color='#3f3f3f')
        self.proxy_rotation_link_entry.grid(row=2, column=0, padx=10, pady=(0, 0), sticky="w")

        self.proxy_rotation_checkbox = customtkinter.CTkCheckBox(self.app_config_frame,
                                                                 text="Proxy rotation",
                                                                 checkbox_width=20,
                                                                 checkbox_height=20,
                                                                 onvalue=True,
                                                                 offvalue=False,
                                                                 command=self.proxy_rotation_checkbox_event)
        self.proxy_rotation_checkbox.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.rpc_url_label = customtkinter.CTkLabel(self.app_config_frame,
                                                    text="RPC url:")
        self.rpc_url_label.grid(row=4, column=0, padx=10, pady=(0, 0), sticky="w")

        self.rpc_url_entry = customtkinter.CTkEntry(self.app_config_frame,
                                                    width=280)
        self.rpc_url_entry.grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

        self.save_config_button = customtkinter.CTkButton(self.app_config_frame,
                                                          text="Save",
                                                          width=70,
                                                          command=self.save_app_config_event)
        self.save_config_button.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        self.load_app_config_from_storage()

        self.tokens_editor_label = customtkinter.CTkLabel(self,
                                                          text="Add token:",
                                                          font=customtkinter.CTkFont(size=14, weight="bold"))
        self.tokens_editor_label.grid(row=6, column=0, padx=15, pady=5, sticky="w")

        self.tokens_editor_frame = customtkinter.CTkFrame(master=self)
        self.tokens_editor_frame.grid(row=7, column=0, padx=15, sticky="nsew")

        self.add_token_symbol_label = customtkinter.CTkLabel(self.tokens_editor_frame,
                                                             text="Symbol:")
        self.add_token_symbol_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")

        self.add_token_symbol_entry = customtkinter.CTkEntry(self.tokens_editor_frame,
                                                             width=70,
                                                             placeholder_text="USDT")
        self.add_token_symbol_entry.grid(row=2, column=0, padx=10, pady=(0, 0), sticky="w")

        self.add_token_cg_id_label = customtkinter.CTkLabel(self.tokens_editor_frame,
                                                            text="CoinGecko id:")
        self.add_token_cg_id_label.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="w")

        self.add_token_cg_id_entry = customtkinter.CTkEntry(self.tokens_editor_frame,
                                                            width=70,
                                                            placeholder_text="tether")
        self.add_token_cg_id_entry.grid(row=2, column=1, padx=10, pady=(0, 0), sticky="w")

        self.input_token_contract_button = customtkinter.CTkButton(self.tokens_editor_frame,
                                                                   text="+",
                                                                   height=20,
                                                                   width=20,
                                                                   command=self.input_token_contract_button_event)
        self.input_token_contract_button.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.add_token_contract_label = customtkinter.CTkLabel(self.tokens_editor_frame,
                                                               text="Input token contract")
        self.add_token_contract_label.grid(row=3, column=0, padx=35, pady=(10, 0), sticky="w")

        self.token_contract_displayer_label = customtkinter.CTkLabel(self.tokens_editor_frame,
                                                                     text="Not imported",
                                                                     text_color="gray",
                                                                     font=customtkinter.CTkFont(size=12,
                                                                                                weight="bold"))
        self.token_contract_displayer_label.grid(row=4, column=0, padx=10, pady=(0, 0), sticky="w")
        self.is_pancake_available_switch = customtkinter.CTkSwitch(self.tokens_editor_frame,
                                                                   text="Pancake swap",
                                                                   onvalue=True,
                                                                   offvalue=False)
        self.is_pancake_available_switch.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")

        self.is_abel_available_switch = customtkinter.CTkSwitch(self.tokens_editor_frame,
                                                                text="Abel swap",
                                                                onvalue=True,
                                                                offvalue=False)
        self.is_abel_available_switch.grid(row=5, column=1, padx=(0, 10), pady=(10, 0), sticky="w")

        self.is_thala_available_switch = customtkinter.CTkSwitch(self.tokens_editor_frame,
                                                                 text="Thala swap",
                                                                 onvalue=True,
                                                                 offvalue=False)
        self.is_thala_available_switch.grid(row=6, column=0, padx=10, pady=(10, 10), sticky="w")

        self.is_liquid_swap_available_switch = customtkinter.CTkSwitch(self.tokens_editor_frame,
                                                                       text="Liquid swap",
                                                                       onvalue=True,
                                                                       offvalue=False)
        self.is_liquid_swap_available_switch.grid(row=6, column=1, padx=(0, 10), pady=(10, 10), sticky="w")

        self.add_token_button = customtkinter.CTkButton(self.tokens_editor_frame,
                                                        text="Add",
                                                        width=70,
                                                        command=self.add_token_button_event)
        self.add_token_button.grid(row=7, column=0, padx=10, pady=(10, 15), sticky="w")

        self.remove_token_label = customtkinter.CTkLabel(self,
                                                         text="Remove token:",
                                                         font=customtkinter.CTkFont(size=14, weight="bold"))
        self.remove_token_label.grid(row=8, column=0, padx=15, pady=5, sticky="w")

        self.remove_token_frame = customtkinter.CTkFrame(master=self)
        self.remove_token_frame.grid(row=9, column=0, padx=15, sticky="nsew")

        self.coin_to_remove_combo_box = customtkinter.CTkComboBox(self.remove_token_frame,
                                                                  width=100,
                                                                  values=self.get_all_token_symbols)
        self.coin_to_remove_combo_box.grid(row=0, column=0, padx=10, pady=(15, 15), sticky="w")

        self.remove_token_button = customtkinter.CTkButton(self.remove_token_frame,
                                                           text="Remove",
                                                           width=70,
                                                           command=self.remove_token_button_event)
        self.remove_token_button.grid(row=0, column=1, padx=10, pady=(15, 15), sticky="w")

    def input_token_contract_button_event(self):
        text = ("Input token contract:\n"
                "(Example:\n"
                "0xf22bede237a07e121b56d91a491eb7bcdfd1f5907926a9e58338f964a01b17fa::asset::USDT)")
        dialog = customtkinter.CTkInputDialog(text=text, title="Input")
        raw_contract = dialog.get_input()

        if not raw_contract:
            return

        if raw_contract is False:
            messagebox.showerror("Error", "Invalid token contract, watch example")
            return

        self.token_contract_to_add = raw_contract
        self.update_token_contract_displayer()

        return raw_contract

    def update_token_contract_displayer(self):
        token_contract = self.token_contract_to_add
        if token_contract:
            short_token_contract = token_contract[:15] + "..." if len(token_contract) > 50 else token_contract
            self.token_contract_displayer_label.configure(text=short_token_contract,
                                                          text_color="#6fc276")
        else:
            self.token_contract_displayer_label.configure(text="Not imported",
                                                          text_color="#F47174")

    def is_token_contract_valid(self):
        try:
            split_contract = self.token_contract_to_add.split('::')
            return len(split_contract) == 3
        except Exception as e:
            print(e)
            return False

    def add_token_button_event(self):
        if not self.add_token_symbol_entry.get():
            messagebox.showerror("Error", "Please input token symbol")
            return

        if self.tokens_editor.is_token_symbol_exist_in_json(self.add_token_symbol_entry.get()):
            messagebox.showerror("Error", "Token symbol already exists")
            return

        if not self.token_contract_to_add:
            messagebox.showerror("Error", "Please input token contract")
            return

        if not self.add_token_cg_id_entry.get():
            messagebox.showerror("Error", "Please input CoinGecko token id, or input 0 if not available")
            return

        token = Token(
            symbol=self.add_token_symbol_entry.get().upper(),
            contract=self.token_contract_to_add,
            is_pancake_available=bool(self.is_pancake_available_switch.get()),
            is_abel_available=bool(self.is_abel_available_switch.get()),
            is_thala_available=bool(self.is_thala_available_switch.get()),
            is_liquid_swap_available=bool(self.is_liquid_swap_available_switch.get()),
            gecko_id=self.add_token_cg_id_entry.get().lower() if self.add_token_cg_id_entry.get() != "0" else None
        )

        token_add_status: bool = self.tokens_editor.add_new_token(token)
        if token_add_status:
            self.update_tokens_combo_box()
            messagebox.showinfo("Success", "Token added successfully")
        else:
            messagebox.showerror("Error", "Token symbol already exists")

    def remove_token_button_event(self):
        if not self.coin_to_remove_combo_box.get():
            messagebox.showerror("Error", "Please select token symbol")
            return

        token_remove_status: bool = self.tokens_editor.remove_token(self.coin_to_remove_combo_box.get())
        if token_remove_status:
            self.update_tokens_combo_box()
            messagebox.showinfo("Success", "Token removed successfully")
        else:
            messagebox.showerror("Error", "Token symbol not found")

    def update_tokens_combo_box(self):
        current_options = self.get_all_token_symbols
        self.balance_checker_coin_option_combobox.configure(values=current_options)
        self.coin_to_remove_combo_box.configure(values=current_options)
        if len(current_options) > 0:
            self.balance_checker_coin_option_combobox.set(current_options[0])
            self.coin_to_remove_combo_box.set(current_options[0])

    def proxy_rotation_checkbox_event(self):
        if self.proxy_rotation_checkbox.get():
            self.proxy_rotation_link_entry.configure(state="normal", fg_color='#343638')
        else:
            self.proxy_rotation_link_entry.configure(textvariable=StringVar(value=""),
                                                     state="disabled",
                                                     fg_color='#3f3f3f')

    def load_app_config_from_storage(self):
        app_config = self.storage.get_app_config()
        if not app_config:
            return

        if app_config.preserve_logs:
            self.preserve_logs_checkbox.select()
        else:
            self.preserve_logs_checkbox.deselect()

        if app_config.mobile_proxy_rotation:
            self.proxy_rotation_checkbox.select()
            self.proxy_rotation_link_entry.configure(state="normal", fg_color='#343638')
            self.proxy_rotation_link_entry.insert(0, app_config.mobile_proxy_rotation_link)
        else:
            self.proxy_rotation_checkbox.deselect()
            self.proxy_rotation_link_entry.configure(state="disabled", fg_color='#3f3f3f')

        if app_config.aptos_rpc_url:
            self.rpc_url_entry.configure(textvariable=StringVar(value=app_config.aptos_rpc_url))

    def save_app_config_event(self):
        app_config = AppConfigSchema()

        if self.proxy_rotation_checkbox.get() is True:
            if not self.proxy_rotation_link_entry.get():
                messagebox.showerror("Error", "Proxy rotation link cannot be empty")
                return

        if not self.rpc_url_entry.get():
            messagebox.showerror("Error", "RPC URL cannot be empty")
            return

        app_config.preserve_logs = self.preserve_logs_checkbox.get()
        app_config.mobile_proxy_rotation = self.proxy_rotation_checkbox.get()
        app_config.mobile_proxy_rotation_link = self.proxy_rotation_link_entry.get()

        self.storage.update_app_config(app_config)
        FileManager().write_data_to_json_file(data=app_config.model_dump(),
                                              file_path=APP_CONFIG_FILE)
        messagebox.showinfo("Success", "App config saved")

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




