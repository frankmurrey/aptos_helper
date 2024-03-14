import tkinter.messagebox
import tkinter.filedialog
from tkinter import Variable
from typing import TYPE_CHECKING

import customtkinter

from gui.objects.float_spinbox import FloatSpinbox

if TYPE_CHECKING:
    from gui.right_frame.actions_components import ActionsFrame


class RunSettingsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any):

        super().__init__(master=master)
        self.master = master

        self.grid(
            row=1,
            column=2,
            padx=20,
            pady=(10, 20),
            sticky="nsew",
            rowspan=2
        )

        self.grid_columnconfigure((0, 1), weight=1)

        self.test_mode_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Test mode",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.test_mode_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.test_mode_checkbox.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        self.shuffle_wallets_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Shuffle wallets",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.shuffle_wallets_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.shuffle_wallets_checkbox.grid(
            row=0,
            column=1,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        self.shuffle_task_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Shuffle tasks",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.shuffle_task_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.shuffle_task_checkbox.grid(
            row=1,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky="ew"
        )

        self.min_delay_label = customtkinter.CTkLabel(
            self,
            text="Min delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.min_delay_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.min_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.min_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=40)
        )
        self.min_delay_entry_spinbox.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        self.max_delay_label = customtkinter.CTkLabel(
            self,
            text="Max delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.max_delay_label.grid(
            row=2,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.max_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=80)
        )
        self.max_delay_entry_spinbox.grid(
            row=3,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        txn_wait_timeout_seconds_label = customtkinter.CTkLabel(
            self,
            text="Wait timeout (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        txn_wait_timeout_seconds_label.grid(
            row=4,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.txn_wait_timeout_seconds_spinbox = FloatSpinbox(self,
                                                             step_size=5,
                                                             width=105)
        self.txn_wait_timeout_seconds_spinbox.entry.configure(
            state="normal",
            textvariable=Variable(value=240)
        )
        self.txn_wait_timeout_seconds_spinbox.add_button.configure(
            state="normal"
        )
        self.txn_wait_timeout_seconds_spinbox.grid(
            row=5,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.wait_for_receipt_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Wait for txn",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.wait_for_txn_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.wait_for_receipt_checkbox.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 10),
            sticky="w"
        )
        self.wait_for_receipt_checkbox.select()

        self.retries_label = customtkinter.CTkLabel(
            self,
            text="Retries:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.retries_label.grid(
            row=4,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.retries_spinbox = FloatSpinbox(self,
                                            start_index=1,
                                            step_size=1,
                                            width=105)
        self.retries_spinbox.entry.configure(
            textvariable=Variable(value=3)
        )
        self.retries_spinbox.grid(
            row=5,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

    def build_config(self):
        run_settings_cfg = {
            "test_mode": self.test_mode_checkbox.get(),
            "min_delay_sec": self.min_delay_entry_spinbox.entry.get(),
            "max_delay_sec": self.max_delay_entry_spinbox.entry.get(),
            "wait_for_receipt": self.wait_for_receipt_checkbox.get(),
            "txn_wait_timeout_sec": self.txn_wait_timeout_seconds_spinbox.entry.get(),
            "shuffle_wallets": self.shuffle_wallets_checkbox.get(),
            "retries": self.retries_spinbox.entry.get()
        }

        return run_settings_cfg

    def upload_from_config(self, run_settings_cfg: dict):
        try:
            if not run_settings_cfg:
                return

            if run_settings_cfg["test_mode"]:
                self.test_mode_checkbox.select()
                self.test_mode_checkbox_event()
            else:
                self.test_mode_checkbox.deselect()
                self.test_mode_checkbox_event()

            if run_settings_cfg["shuffle_wallets"]:
                self.shuffle_wallets_checkbox.select()
                self.shuffle_wallets_checkbox_event()
            else:
                self.shuffle_wallets_checkbox.deselect()
                self.shuffle_wallets_checkbox_event()

            self.min_delay_entry_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["min_delay_sec"])
            )
            self.max_delay_entry_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["max_delay_sec"])
            )

            if run_settings_cfg['wait_for_receipt']:
                self.wait_for_receipt_checkbox.select()
                self.wait_for_txn_checkbox_event()
                self.txn_wait_timeout_seconds_spinbox.entry.configure(
                    textvariable=Variable(value=run_settings_cfg["txn_wait_timeout_sec"])
                )
            else:
                self.wait_for_receipt_checkbox.deselect()
                self.wait_for_txn_checkbox_event()

            self.retries_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["retries"])
            )

        except Exception as e:
            tkinter.messagebox.showerror(
                title="Error",
                message=str(e)
            )

    def wait_for_txn_checkbox_event(self):
        if self.wait_for_receipt_checkbox.get():
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="normal",
                fg_color="gray16",
                textvariable=Variable(value=120)
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="normal")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="normal")
        else:
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="disabled",
                fg_color="#3f3f3f",
                textvariable=Variable(value="")
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="disabled")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="disabled")

    def test_mode_checkbox_event(self):
        if self.test_mode_checkbox.get():
            self.test_mode_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.test_mode_checkbox.configure(
                text_color="#F47174"
            )

    def shuffle_wallets_checkbox_event(self):
        if self.shuffle_wallets_checkbox.get():
            self.shuffle_wallets_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.shuffle_wallets_checkbox.configure(
                text_color="#F47174"
            )

    def shuffle_task_checkbox_event(self):
        if self.shuffle_task_checkbox.get():
            self.shuffle_task_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.shuffle_task_checkbox.configure(
                text_color="#F47174"
            )