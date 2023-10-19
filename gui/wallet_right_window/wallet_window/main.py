import tkinter
import tkinter.messagebox
from typing import Callable, Union

import customtkinter
from pydantic import ValidationError
from aptos_sdk.account import AccountAddress

from src.schemas.wallet_data import WalletData
from src.schemas.proxy_data import ProxyData
from contracts.tokens.main import Tokens

from gui import objects
from gui.wallet_right_window.wallet_window.empty_wallet_data import EmptyUiWalletData
from gui.wallet_right_window.wallet_window.private_key_entry import PrivateKeyEntry
from gui.wallet_right_window.wallet_window.address_entry import AddressEntry
from gui.wallet_right_window.wallet_window.pair_address_entry import PairAddressEntry
from src.schemas.app_config import AppConfigSchema
from src.proxy_manager import ProxyManager
from src.storage import Storage
from utils.balance_checker import BalanceChecker


class WalletFrame(customtkinter.CTkFrame):

    def __init__(
            self,
            master,
            on_wallet_save: Callable[[Union[WalletData, None]], None],
            wallet_data: WalletData = None,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.wallet_data = wallet_data
        if self.wallet_data is None:
            self.wallet_data = EmptyUiWalletData()

        self.on_wallet_save = on_wallet_save

        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(6, weight=1)

        # NAME
        self.name_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Name",
            textvariable=tkinter.StringVar(value=self.wallet_data.name),
            width=200,
        )
        self.name_entry.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        # PRIVATE KEY
        self.private_key_entry = PrivateKeyEntry(
            self,
            private_key=self.wallet_data.private_key,
        )
        self.private_key_entry.grid(row=1, column=0, padx=10, pady=0, sticky="w")

        # ADDRESS
        self.address_entry = AddressEntry(
            self,
            address=self.wallet_data.address,
        )
        self.address_entry.grid(row=2, column=0, padx=10, pady=0, sticky="w")
        self.private_key_entry.set_focus_in_callback(self.address_entry.show_full_text)
        self.private_key_entry.set_focus_out_callback(self.address_entry.hide_full_text)
        self.private_key_entry.set_text_changed_callback(
            lambda: self.address_entry.set_address(
                self.private_key_entry.private_key,
            )
        )

        # PAIR ADDRESS
        self.pair_address_entry = PairAddressEntry(
            self,
            pair_address=self.wallet_data.pair_address,
        )
        self.pair_address_entry.grid(row=3, column=0, padx=10, pady=0, sticky="w")

        # PROXY
        self.proxy_entry = objects.CTkEntryWithLabel(
            self,
            label_text="Proxy",
            textvariable=tkinter.StringVar(
                value=self.wallet_data.proxy.to_string() if isinstance(self.wallet_data.proxy, ProxyData) else ""
            ),
            width=200,
        )
        self.proxy_entry.grid(row=4, column=0, padx=10, pady=0, sticky="w")

        # ADD BUTTON
        self.add_button = customtkinter.CTkButton(
            self,
            text="Save",
            command=self.save_wallet_button_clicked,
        )
        self.add_button.grid(row=7, column=0, padx=10, pady=10, sticky="ws")

        self.__last_private_key_repr = ""
        self.__private_key = ""

    def toggle_wallet_type(self):
        try:
            self.address_entry.set_address(
                self.private_key_entry.private_key,
            )
            self.private_key_entry.disable_invalid_warning()

        except ValueError as e:
            self.private_key_entry.enable_invalid_warning()
            return

    def toggle_cairo_version(self):
        try:
            self.address_entry.set_address(
                self.private_key_entry.private_key,
            )
            self.private_key_entry.disable_invalid_warning()

        except ValueError as e:
            self.private_key_entry.enable_invalid_warning()
            return

    def get_wallet_data(self) -> WalletData:

        name = self.name_entry.get().strip()

        private_key = self.private_key_entry.private_key
        pair_address = self.pair_address_entry.pair_address

        proxy = self.proxy_entry.get().strip()

        wallet_data = WalletData(
            name=name,
            private_key=private_key,
            pair_address=pair_address,
            proxy=proxy,
        )

        return wallet_data

    def save_wallet_button_clicked(self):
        wallet_data = None

        try:
            wallet_data = self.get_wallet_data()
        except ValidationError as e:
            error_messages = e.errors()[0]["msg"]
            tkinter.messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            self.focus_force()

        self.on_wallet_save(wallet_data)


class WalletWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            wallet_data: WalletData = None,
            on_wallet_save: Callable[[WalletData], None] = None
    ):
        super().__init__(master)

        self.title("Add wallet")
        self.geometry("340x360")

        self.after(10, self.focus_force)

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = WalletFrame(
            self,
            on_wallet_save=on_wallet_save,
            wallet_data=wallet_data
        )

    def close(self):
        self.frame.destroy()
        self.destroy()


class TokenSelectWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            wallet_items: list,
    ):
        super().__init__(master)

        self.title("Select token")
        self.geometry("240x160+500+400")

        self.after(10, self.focus_force)

        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = TokenSelectFrame(
            self,
            wallet_items=wallet_items,
        )

    def close(self):
        self.frame.destroy()
        self.destroy()


class TokenSelectFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            wallet_items: list,
    ):
        super().__init__(master)

        self.wallet_items = wallet_items

        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)

        self.token_option = customtkinter.CTkComboBox(
            self,
            values=self.token_options,
            width=120,
        )
        self.token_option.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.use_wallet_proxy_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use wallet proxy",
            checkbox_width=20,
            checkbox_height=20,
            onvalue=True,
            offvalue=False,
        )
        self.use_wallet_proxy_checkbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

        self.load_button = customtkinter.CTkButton(
            self,
            text="Load",
            width=110,
            command=self.load_button_event,
        )
        self.load_button.grid(row=2, column=0, padx=10, pady=10, sticky="ws")

    @property
    def token_options(self):
        token_objs = Tokens()._get_all_token_objs()
        return [token_obj.symbol.upper() for token_obj in token_objs]

    def load_button_event(self):

        token = self.token_option.get()
        use_wallet_proxy = self.use_wallet_proxy_checkbox.get()
        if not token:
            return

        storage = Storage()
        app_config: AppConfigSchema = storage.app_config

        for wallet_item in self.wallet_items:
            proxy = None
            if use_wallet_proxy:
                pm = ProxyManager(wallet_item.wallet_data.proxy)
                proxy = pm.get_proxy() if wallet_item.wallet_data.proxy else None

            checker = BalanceChecker(
                base_url=app_config.rpc_url,
                coin_symbol=token.lower(),
                proxies=proxy
            )
            balance = checker.get_balance_decimals(AccountAddress.from_hex(wallet_item.wallet_data.address))
            balance = round(balance, 4)
            wallet_item.set_wallet_balance(balance=balance, token_symbol=token)

