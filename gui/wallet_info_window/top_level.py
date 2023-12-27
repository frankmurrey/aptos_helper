from typing import List, TYPE_CHECKING

import customtkinter
from PIL import Image

from gui.wallet_info_window.scrollable_frame import WalletInfoScrollableFrame
from gui.wallet_info_window.table_top import WalletInfoTopFrame

from src import paths
from src.schemas import tasks
from src.schemas.wallet_data import WalletData

if TYPE_CHECKING:
    from gui.right_frame.wallets_table_frame import WalletsTable


class WalletInfoWindow(customtkinter.CTkToplevel):
    def __init__(self, master, wallet_data: WalletData):
        super().__init__(master)

        self.master: 'WalletsTable' = master
        self.wallet_data = wallet_data

        self.title("Wallet Info")
        self.geometry("800x600")

        self.after(10, self.focus_force)
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=0)

        self.protocol("WM_DELETE_WINDOW", self.close)

        # WALLET ADDRESS
        self.wallet_data_label = customtkinter.CTkLabel(
            self,
            text=f"Wallet address:",
            font=("Arial", 14, "bold"),
        )
        self.wallet_data_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0),
        )

        self.wallet_address_value_label = customtkinter.CTkLabel(
            self,
            text=f"{self.wallet_data.address}",
            font=("Arial", 14, "bold"),
        )
        self.wallet_address_value_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 10),
        )

        # REFRESH BUTTON
        self.refresh_image = customtkinter.CTkImage(
            light_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button.png"),
            dark_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button.png"),
            size=(20, 20)
        )
        self.refresh_image_active = customtkinter.CTkImage(
            light_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button_active.png"),
            dark_image=Image.open(f"{paths.GUI_DIR}/images/refresh_button_active.png"),
            size=(20, 20)
        )

        self.refresh_button = customtkinter.CTkButton(
            self,
            image=self.refresh_image,
            command=self.refresh_data_event,
            hover=False,
            text="- refresh data",
            bg_color='transparent',
            fg_color='transparent',
            width=5,
            text_color='gray58',

        )
        self.refresh_button.grid(
            row=0,
            column=0,
            sticky="e",
            padx=20,
            pady=(10, 0)
        )

        # TOP FRAME
        self.top_frame = WalletInfoTopFrame(
            self,
            grid={
                "row": 2,
                "column": 0,
                "sticky": "ew",
                "padx": 10,
                "pady": 10,
            }
        )

        # SCROLLABLE FRAME
        self.scrollable_frame = WalletInfoScrollableFrame(
            self,
            grid={
                "row": 3,
                "column": 0,
                "sticky": "nsew",
                "padx": 10,
                "pady": 10,
            }
        )
        self.scrollable_frame.draw_frame(tasks=self.info_items)

    @property
    def info_items(self) -> List['tasks.TaskBase']:
        actions = self.master.master.actions_frame.get_wallet_actions(
            wallet_id=self.wallet_data.wallet_id
        )
        return actions

    def close(self):
        self.scrollable_frame.destroy()
        self.destroy()

    def refresh_data_event(self):
        self.refresh_button.configure(text="Refreshing...")
        self.set_new_data()
        self.refresh_button.configure(text="- refresh data")

    def set_refresh_image(self, state: bool):
        if state:
            self.refresh_button.configure(image=self.refresh_image_active, text="- refreshing...")
        else:
            self.refresh_button.configure(image=self.refresh_image, text="- refresh data")

    def set_new_data(self):
        try:
            wallet_tasks = self.master.master.actions_frame.get_wallet_actions(
                wallet_id=self.wallet_data.wallet_id
            )
            self.scrollable_frame.draw_frame(tasks=wallet_tasks)

        except Exception as e:
            return
