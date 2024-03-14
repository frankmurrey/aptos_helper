from tkinter import messagebox, Variable

import customtkinter
from pydantic.error_wrappers import ValidationError

from src.schemas import tasks
from gui.modules.txn_settings_frame import TxnSettingFrame
from gui.objects import CTkCustomTextBox


class NftCollectTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.NftCollectTask = None,
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        collect_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.collect_frame = NftCollectFrame(
            master=self.tabview.tab(tab_name),
            grid=collect_frame_grid,
            task=task
        )

        txn_settings_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_grid
        )

        text_box_grid = {
            "row": 2,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "ew"
        }

        text = (f"Will transfer all V2 nfts found in wallet,\n\n"
                f"Recipient should be specified as 'Pair Address',\n"
                f"while adding/importing wallet.")

        self.info_textbox = CTkCustomTextBox(
            master=self.tabview.tab(tab_name),
            grid=text_box_grid,
            text=text,
        )

    def build_config_data(self):
        try:
            config_data = tasks.NftCollectTask(
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                min_delay_nft_transfer_sec=self.collect_frame.min_delay_entry.get(),
                max_delay_nft_transfer_sec=self.collect_frame.max_delay_entry.get(),
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class NftCollectFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.NftCollectTask,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.grid_rowconfigure((0, 1), weight=1)

        # DELAY LABEL
        self.delay_label = customtkinter.CTkLabel(
            self,
            text="Delay between transfers if multiple NFT found:",
            font=("Arial", 14, "bold")
        )
        self.delay_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w", columnspan=2)

        # MIN DELAY
        self.min_delay_label = customtkinter.CTkLabel(self, text="Min delay sec:")
        self.min_delay_label.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")

        min_delay = getattr(self.task, "min_delay_nft_transfer_sec", 10)
        self.min_delay_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=min_delay))
        self.min_delay_entry.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        # MAX DELAY
        self.max_delay_label = customtkinter.CTkLabel(self, text="Max delay sec:")
        self.max_delay_label.grid(row=1, column=1, padx=20, pady=(5, 0), sticky="w")

        max_delay = getattr(self.task, "max_delay_nft_transfer_sec", 20)
        self.max_delay_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=20))
        self.max_delay_entry.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="w")
