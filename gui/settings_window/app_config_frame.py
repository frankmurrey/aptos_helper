import tkinter
from tkinter import messagebox

import customtkinter

from src import paths
from src import enums
from src import exceptions
from src.storage import Storage
from src.schemas.app_config import AppConfigSchema
from utils.file_manager import FileManager
from gui.modules.frames import FloatSpinbox


class AppConfigFrame(customtkinter.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.app_config: AppConfigSchema = Storage().app_config

        self.label = customtkinter.CTkLabel(
            master=self,
            text="App config:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=15)

        self.run_mode_label = customtkinter.CTkLabel(
            master=self, text="Run mode:", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.run_mode_label.grid(row=1, column=0, sticky="w", pady=(5, 0), padx=15)

        run_mode = self.app_config.run_mode
        self.run_mode_combobox = customtkinter.CTkComboBox(
            master=self,
            width=100,
            font=customtkinter.CTkFont(size=12),
            values=[
                enums.RunMode.SYNC.upper(),
                enums.RunMode.ASYNC.upper(),
            ],
        )
        self.run_mode_combobox.set(run_mode.upper())
        self.run_mode_combobox.grid(row=2, column=0, sticky="w", pady=(0, 15), padx=15)

        is_preserve_on = self.app_config.preserve_logs
        self.preserve_logs_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Preserve logs",
            variable=tkinter.Variable(value=is_preserve_on),
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            text_color="#6fc276" if is_preserve_on else "#F47174",
            onvalue=True,
            offvalue=False,
            command=self.preserve_logs_checkbox_event
        )
        self.preserve_logs_checkbox.grid(row=3, column=0, sticky="wn", pady=10, padx=15)

        self.aptos_rpc_url_label = customtkinter.CTkLabel(
            master=self, text="Aptos RPC URL:", font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.aptos_rpc_url_label.grid(row=4, column=0, sticky="w", pady=(5, 0), padx=15)

        self.aptos_rpc_url_entry = customtkinter.CTkEntry(
            master=self,
            width=280,
            font=customtkinter.CTkFont(size=12),
            textvariable=tkinter.StringVar(value=self.app_config.rpc_url),
        )
        self.aptos_rpc_url_entry.grid(row=5, column=0, sticky="w", pady=(0, 15), padx=15)

        self.wallets_amount_to_execute_in_test_mode_label = customtkinter.CTkLabel(
            master=self,
            text="Wallets amount to execute in test mode:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallets_amount_to_execute_in_test_mode_label.grid(row=6, column=0, sticky="w", pady=(5, 0), padx=15)

        self.wallets_amount_to_execute_in_test_mode_spinbox = FloatSpinbox(
            master=self,
            step_size=1,
            width=110,
            start_index=1
        )
        self.wallets_amount_to_execute_in_test_mode_spinbox.entry.configure(
            textvariable=tkinter.Variable(value=self.app_config.wallets_amount_to_execute_in_test_mode))

        self.wallets_amount_to_execute_in_test_mode_spinbox.grid(
            row=7, column=0, sticky="w", pady=(0, 20), padx=15
        )

        use_proxy = self.app_config.use_proxy
        self.use_proxy_checkbox = customtkinter.CTkCheckBox(
            master=self,
            text="Use proxy",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            text_color="#6fc276" if use_proxy else "#F47174",
            onvalue=True,
            offvalue=False,
            command=self.use_proxy_checkbox_event,
        )
        self.use_proxy_checkbox.grid(row=8, column=0, sticky="w", pady=(0, 20), padx=15)
        self.use_proxy_checkbox.select() if use_proxy else self.use_proxy_checkbox.deselect()

        self.save_button = customtkinter.CTkButton(
            master=self,
            text="Save",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.save_button_event
        )
        self.save_button.grid(row=9, column=0, sticky="w", pady=15, padx=15)

    def preserve_logs_checkbox_event(self):
        if self.preserve_logs_checkbox.get():
            self.preserve_logs_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.preserve_logs_checkbox.configure(
                text_color="#F47174"
            )

    def use_proxy_checkbox_event(self):
        if self.use_proxy_checkbox.get():
            self.use_proxy_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.use_proxy_checkbox.configure(
                text_color="#F47174"
            )

    def save_button_event(self):
        try:
            app_config = AppConfigSchema(
                preserve_logs=self.preserve_logs_checkbox.get(),
                rpc_url=self.aptos_rpc_url_entry.get(),
                wallets_amount_to_execute_in_test_mode=self.wallets_amount_to_execute_in_test_mode_spinbox.get(),
            )
            Storage().update_app_config(app_config)
            self.app_config = app_config
            try:
                FileManager.write_data_to_json_file(
                    file_path=paths.APP_CONFIG_FILE,
                    data=app_config.dict(),
                    raise_exception=True
                )
                messagebox.showinfo(
                    title="Success",
                    message="App config saved successfully"
                )

            except exceptions.AppValidationError as e:
                messagebox.showerror(
                    title="Config validation error", message=e.message
                )
                return None

        except exceptions.ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None
