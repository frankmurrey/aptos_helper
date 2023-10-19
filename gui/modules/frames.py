from typing import Callable, Union
from tkinter import Variable

from gui.modules.swap import SwapTab

import customtkinter


class ModulesFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(
            row=0,
            column=2,
            padx=20,
            pady=20,
            sticky="nsew")
        self.frame.grid_rowconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(self.frame, width=300)
        self.tabview.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="nsew",
            rowspan=7
        )
        self.tabview.grid_columnconfigure(0, weight=1)
        self.set_default_tab()

    def set_default_tab(self):
        tab_name = "Swap"
        self.tabview.add(tab_name)
        self.tabview.set(tab_name)
        SwapTab(
            self.tabview,
            tab_name
        )


class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(
            self,
            *args,
            width: int = 100,
            height: int = 32,
            start_index: int = 0,
            step_size: Union[int, float] = 1,
            command: Callable = None,
            **kwargs
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = int(step_size)
        self.start_index = int(start_index)
        self.command = command

        self.configure(fg_color=("gray78", "gray21"))

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, fg_color="gray16")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, str(start_index))

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            if value < self.start_index:
                value = self.start_index
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))

    def set_normal_state(self, value: float):
        self.entry.configure(
            state="normal",
            fg_color="gray16",
            textvariable=Variable(value=value)
        )
        self.add_button.configure(
            state="normal")

        self.subtract_button.configure(
            state="normal")

    def set_disabled_state(self):
        self.entry.configure(
            state="disabled",
            fg_color="#3f3f3f",
            textvariable=Variable(value="")
        )
        self.add_button.configure(
            state="disabled")

        self.subtract_button.configure(
            state="disabled")
