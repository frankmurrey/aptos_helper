import tkinter
import tkinter.messagebox

import customtkinter

from gui import objects, constants
import config


class PairAddressEntry(objects.CTkEntryWithLabel):
    def __init__(
            self,
            master,
            pair_address: str,
            **kwargs
    ):
        super().__init__(
            master,
            label_text="Pair address",
            textvariable=tkinter.StringVar(value=pair_address),
            width=200,

            hide_on_focus_out=True,

            on_text_changed=self.pair_address_changed,

            **kwargs
        )

        # INVALID LABEL
        self.info_label = customtkinter.CTkLabel(
            self,
            text="",
            text_color=constants.ERROR_HEX,
        )
        self.info_label.grid(row=1, column=1, padx=10, pady=0, sticky="w")

    @property
    def pair_address(self):
        return self.text

    def set_invalid_label(self):
        self.info_label.configure(
            text="Invalid address",
            text_color=constants.ERROR_HEX,
        )

    def set_aptos_label(self):
        self.info_label.configure(
            text="APTOS",
            text_color=constants.SUCCESS_HEX,
        )

    def set_evm_label(self):
        self.info_label.configure(
            text="EVM",
            text_color=constants.SUCCESS_HEX,
        )

    def set_empty_label(self):
        self.info_label.configure(
            text="",
        )

    def pair_address_changed(self):

        if len(self.text) == config.APTOS_KEY_LENGTH:
            self.set_aptos_label()

        elif len(self.text) == config.EVM_ADDRESS_LENGTH:
            self.set_evm_label()

        elif not len(self.text):
            self.set_empty_label()

        else:
            self.set_invalid_label()
