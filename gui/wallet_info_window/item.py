import customtkinter

import config
from src.schemas.tasks.base.base import TaskBase

from gui import constants
from gui.objects import LinkButton
from gui.wallet_info_window.status_info_window import StatusInfoWindow


class WalletInfoItem(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            task: TaskBase,
            grid,
            **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.master = master
        self.task = task

        self.configure(fg_color="grey20")
        self.grid(**grid)

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="uniform")
        self.grid_rowconfigure(0, weight=1)

        # MODULE NAME
        self.module_name_label = customtkinter.CTkLabel(
            self,
            text=task.module_name.title(),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.module_name_label.grid(
            row=0,
            column=0,
            padx=(20, 0),
            pady=3,
            sticky="ew",
        )

        # MODULE TYPE
        self.module_type_label = customtkinter.CTkLabel(
            self,
            text=task.module_type.title(),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.module_type_label.grid(
            row=0,
            column=1,
            padx=(0, 0),
            pady=3,
            sticky="ew",
        )

        # STATUS
        self.status_label = customtkinter.CTkLabel(
            self,
            text=task.task_status.upper(),
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.status_label.grid(
            row=0,
            column=2,
            padx=(0, 0),
            pady=5,
            sticky="ew",
        )

        # STATUS INFO
        self.status_info_window = None

        status_info_grid = {
            "row": 0,
            "column": 3,
            "padx": (0, 0),
            "pady": 5,
            "sticky": "ew",
        }
        if task.result_info:

            self.status_info_element = customtkinter.CTkButton(
                self,
                text="View",
                command=self.status_button_event,
                font=customtkinter.CTkFont(size=12, weight="bold", underline=True),
                fg_color='transparent',
                bg_color='transparent',
                text_color=constants.LINK_COLOR_HEX,
                hover=False
            )
            self.status_info_element.grid(**status_info_grid)

        else:
            self.status_info_element = customtkinter.CTkLabel(
                self,
                text="N/A",
                font=customtkinter.CTkFont(size=12, weight="bold")
            )
            self.status_info_element.grid(**status_info_grid)

        # TXN HASH
        hash_grid = {
            "row": 0,
            "column": 4,
            "padx": (0, 0),
            "pady": 5,
            "sticky": "ew",
        }

        if task.result_hash:

            self.txn_hash_element = LinkButton(
                master=self,
                link=f"{config.EXPLORER_BASE_URL}/tx/{task.result_hash}",
                grid=hash_grid,
            )

        else:
            self.txn_hash_element = customtkinter.CTkLabel(
                self,
                text="N/A",
                font=customtkinter.CTkFont(size=12, weight="bold")
            )
            self.txn_hash_element.grid(**hash_grid)

    def status_button_event(self):
        self.status_info_window = StatusInfoWindow(
            master=self.master,
            info=self.task.result_info,
        )
        self.status_info_window.focus_force()
