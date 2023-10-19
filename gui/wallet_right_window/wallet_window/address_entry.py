import tkinter
import tkinter.messagebox
from aptos_sdk.account import Account

import config
from gui import objects


class AddressEntry(objects.CTkEntryWithLabel):
    def __init__(
            self,
            master,
            address: str,
            **kwargs
    ):
        super().__init__(
            master,
            label_text="Address",
            textvariable=tkinter.StringVar(value=address),
            width=200,
            state=tkinter.DISABLED,

            hide_on_focus_out=True,

            **kwargs
        )

    def set_address(
            self,
            private_key: str,
    ):
        if len(private_key) != config.APTOS_KEY_LENGTH:
            return

        address = Account.load_key(private_key).address()

        self.entry.configure(textvariable=tkinter.StringVar(value=str(address)))
