import tkinter.messagebox
import tkinter.filedialog
from typing import List, Union

import customtkinter

from gui.wallet_right_window.wallet_window import WalletWindow
from gui.wallet_right_window.wallet_window import TokenSelectWindow
from gui.wallet_right_window.wallets_table import WalletsTable
from gui.wallet_right_window.actions_frame import ActionsFrame
from src.schemas.wallet_data import WalletData
from src.wallet_manager import WalletManager
from src.file_manager import FileManager
from src import paths


class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master: any, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.actions_top_level_window = None

        self.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.grid_rowconfigure(8, weight=0)
        self.grid_rowconfigure(9, weight=1)

        self.wallets_table = WalletsTable(self, width=1100)

        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.grid(row=8, column=0, padx=20, pady=2, sticky="nsew")

        self.import_button = customtkinter.CTkButton(
            self.button_frame,
            text="Import",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=100,
            height=30,
            command=self.load_wallets_csv_file,
        )
        self.import_button.grid(row=0, column=0, padx=20, pady=10, sticky="wn")

        self.add_wallet_button = customtkinter.CTkButton(
            self.button_frame,
            text="Add wallet",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=100,
            height=30,
            command=self.add_wallet_button_clicked,
        )
        self.add_wallet_button.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="wn")

        self.remove_button = customtkinter.CTkButton(
            self.button_frame,
            text="Remove all",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            fg_color="#db524b",
            hover_color="#5e1914",
            width=100,
            height=30,
            command=self.remove_all_wallets,
        )

        self.remove_button.grid(row=0, column=2, padx=0, pady=10, sticky="wn")

        self.selected_wallets_label = customtkinter.CTkLabel(
            self.button_frame,
            text="Selected: 0",
            font=customtkinter.CTkFont(size=12, weight="bold"),
        )
        self.selected_wallets_label.grid(row=0, column=3, padx=20, pady=10, sticky="wn")

        self.actions_frame = ActionsFrame(self)
        self.actions_frame.grid(row=9, column=0, padx=20, pady=10, sticky="nsew")

        # ADD WALLET
        self.add_wallet_window = None

        # BALANCE CHECK
        self.token_select_window = None

    @property
    def wallets(self):
        return [
            wallet_item.wallet_data for wallet_item in self.wallets_table.wallets_items
        ]

    def add_wallet_button_clicked(self):
        if self.add_wallet_window is not None:
            return

        self.add_wallet_window = WalletWindow(
            master=self.master,
            on_wallet_save=self.add_wallet_callback,
        )
        self.add_wallet_window.frame.name_entry.entry.configure(
            textvariable=tkinter.StringVar(value=f"Wallet {len(self.wallets) + 1}")
        )

        self.add_wallet_window.protocol(
            "WM_DELETE_WINDOW", self.close_add_wallet_window
        )

    def set_wallets(self, wallets: List[WalletData]):

        if not len(self.wallets):
            self.wallets_table.set_wallets(wallets)
            return

        remove_previous_wallets = tkinter.messagebox.askyesno(
            title="Remove previous wallets",
            message="Remove previous wallets?",
            icon="warning",
        )

        if not remove_previous_wallets:
            self.wallets_table.add_wallets(wallets)
        else:
            self.wallets_table.set_wallets(wallets)

    def load_wallets_csv_file(self):
        filepath = tkinter.filedialog.askopenfilename(
            initialdir=paths.MAIN_DIR,
            title="Select wallets csv file",
            filetypes=[("Text files", "*.csv")],
        )

        if not filepath:
            return

        wallets_raw_data = FileManager.read_data_from_csv_file(filepath)
        wallets = WalletManager.get_wallets(wallets_raw_data)
        if wallets is None:
            return None

        self.set_wallets(wallets)

    def remove_all_wallets(self):

        if not self.wallets:
            return

        msg_box = tkinter.messagebox.askyesno(
            title="Remove all",
            message="Are you sure you want to remove all wallets?",
            icon="warning",
        )

        if not msg_box:
            return

        self.wallets_table.remove_all_wallets()
        self.wallets_table.update_selected_wallets_labels()

    def add_wallet_callback(self, wallet_data: Union[WalletData, None]):
        if wallet_data is None:
            return

        self.wallets_table.add_wallets([wallet_data])
        self.close_add_wallet_window()

    def close_add_wallet_window(self):
        self.add_wallet_window.close()
        self.add_wallet_window = None

    def close_balances_window(self):
        self.token_select_window.close()
        self.token_select_window = None
