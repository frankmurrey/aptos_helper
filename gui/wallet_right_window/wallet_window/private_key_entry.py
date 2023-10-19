import tkinter
import tkinter.messagebox

import customtkinter

from gui import objects
from gui import constants
import config


class PrivateKeyEntry(objects.CTkEntryWithLabel):
    def __init__(
            self,
            master,
            private_key: str,
            **kwargs
    ):
        super().__init__(
            master,
            label_text="Private key*",
            textvariable=tkinter.StringVar(value=private_key),
            width=200,

            hide_on_focus_out=True,

            on_text_changed=self.private_key_changed,

            **kwargs
        )

        # INVALID LABEL
        self.invalid_entry_label = customtkinter.CTkLabel(
            self,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.invalid_entry_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

    @property
    def private_key(self):
        return self.text

    def disable_invalid_warning(self):
        self.invalid_entry_label.configure(text="")

    def enable_invalid_warning(self):
        self.invalid_entry_label.configure(text="Invalid key")

    def private_key_changed(self):

        if len(self.text) == config.APTOS_KEY_LENGTH:
            self.disable_invalid_warning()

        elif not len(self.text):
            self.disable_invalid_warning()

        else:
            self.enable_invalid_warning()
