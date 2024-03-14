import asyncio
import tkinter
import tkinter.messagebox
from typing import Callable, Union, List, TYPE_CHECKING

from src.schemas.tasks import TaskBase

import customtkinter

from gui.wallet_info_window.item import WalletInfoItem

if TYPE_CHECKING:
    from gui.wallet_info_window.window import WalletInfoWindow


class WalletInfoScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master,
            grid,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.master: 'WalletInfoWindow' = master

        self.current_items: List['WalletInfoItem'] = []

        self.grid(**grid)

        self.grid_columnconfigure(0, weight=1)

    def clear_frame(self):
        if not self.current_items:
            return

        for item in self.current_items:
            item.grid_forget()
            item.destroy()

        self.current_items.clear()

    def draw_frame(self, tasks: List['TaskBase']):
        self.clear_frame()

        start_row = 0
        start_column = 0

        for task_index, task in enumerate(tasks):
            item = WalletInfoItem(
                self,
                task=task,
                grid={
                    "row": start_row + task_index,
                    "column": start_column,
                    "sticky": "ew",
                    "padx": 5,
                    "pady": 3,
                }
            )
            self.current_items.append(item)
