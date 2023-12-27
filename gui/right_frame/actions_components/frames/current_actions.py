from typing import TYPE_CHECKING

import customtkinter


if TYPE_CHECKING:
    from gui.right_frame.actions_components.frames.actions import ActionsFrame


class CurrentActionsFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.master: 'ActionsFrame' = master

        self.grid(
            row=1,
            column=0,
            padx=20,
            pady=(10, 20),
            sticky="nsew"
        )
        self.grid_columnconfigure(0, weight=1)

        self.no_actions_label = customtkinter.CTkLabel(
            self,
            text="No actions",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.no_actions_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=10
        )