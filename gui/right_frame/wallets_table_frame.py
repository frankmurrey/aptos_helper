from typing import List, Union
from uuid import UUID

import customtkinter

from gui.right_frame.wallet_components.wallet_item import WalletItem
from gui.right_frame.wallets_table_top_frame import WalletsTableTop
from src.schemas.wallet_data import WalletData


class WalletsTable(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.grid(row=1, column=0, padx=20, pady=0, sticky="nsew", rowspan=7)

        self.no_wallets_label = customtkinter.CTkLabel(
            self,
            text="No wallets",
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

        self.grid_columnconfigure(0, weight=1)

        self.wallets_items: List[WalletItem] = []

        table_grid = {"row": 0, "column": 0, "padx": 20, "pady": (0, 0), "sticky": "ew"}
        self.wallets_table_top = WalletsTableTop(
            master=master, grid=table_grid, wallet_items=self.wallets_items
        )

    @property
    def wallets(self):
        return [wallet_item.wallet_data for wallet_item in self.wallets_items]

    @property
    def selected_wallets(self):
        return [wallet_item.wallet_data for wallet_item in self.wallets_items if wallet_item.is_chosen]

    def get_wallet_item_by_wallet_id(self, wallet_id: UUID) -> Union[WalletItem, None]:
        if self.wallets_items:
            for wallet_item in self.wallets_items:
                if wallet_item.wallet_data.wallet_id == wallet_id:
                    return wallet_item

        return None

    def update_selected_wallets_labels(self):
        self.master.selected_wallets_label.configure(text=f"Selected: {len(self.selected_wallets)}")

    def remove_all_wallets(self, show_no_wallets: bool = True):
        if not len(self.wallets):
            return

        for wallet_index, wallet_item in enumerate(self.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

        self.wallets_items.clear()

        if show_no_wallets:
            self.show_no_wallets_label()

    def show_no_wallets_label(self):
        self.no_wallets_label = customtkinter.CTkLabel(
            self,
            text="No wallets, why delete me?",
            font=customtkinter.CTkFont(size=20, weight="bold"),
            corner_radius=10,
        )
        self.no_wallets_label.grid(row=0, column=0, padx=20, pady=20, sticky="ns")

    def destroy_no_wallets_label(self):
        if self.no_wallets_label is None:
            return

        self.no_wallets_label.grid_forget()
        self.no_wallets_label.destroy()
        self.no_wallets_label = None

    def remove_selected_wallets(self):
        new_wallets_data = []
        for wallet_index, wallet_item in enumerate(self.wallets_items):
            wallet_item.grid_forget()
            wallet_item.frame.destroy()
            wallet_item.destroy()

            if not wallet_item.is_chosen:
                new_wallets_data.append(wallet_item.wallet_data)

        self.set_wallets(new_wallets_data)

    def set_wallets(self, wallets: List[WalletData]):
        """
        Set wallets
        Args:
            wallets:

        Returns:

        """

        self.destroy_no_wallets_label()
        self.remove_all_wallets(show_no_wallets=False)

        start_row = 0
        start_column = 0

        wallets_items = []
        for wallet_index, wallet_data in enumerate(wallets):
            wallet_item_grid = {
                "row": start_row + 1 + wallet_index,
                "column": start_column,
                "padx": 10,
                "pady": 3,
                "sticky": "ew",
            }

            if not wallet_data.name:
                wallet_data.name = f"Wallet {wallet_index + 1}"

            wallet_item = WalletItem(
                master=self,
                grid=wallet_item_grid,
                wallet_data=wallet_data,
                index=wallet_index,
            )
            wallets_items.append(wallet_item)

        self.wallets_items = wallets_items
        self.wallets_table_top.wallet_items = self.wallets_items

    def add_wallets(self, wallets: List[WalletData]):
        """
        Add wallets to existing wallets
        Args:
            wallets: List of wallets
        Returns: None
        """
        wallets = [*self.wallets, *wallets]
        self.set_wallets(wallets)
