import tkinter
from typing import Optional, Callable, Union

import customtkinter

from utils import gui as gui_utils


class CTkEntryWithLabel(customtkinter.CTkFrame):
    """
    Entry with a label
    """

    def __init__(
            self,
            master,
            label_text: str,

            textvariable: Optional[Union[tkinter.StringVar, tkinter.Variable]] = None,

            on_text_changed: Optional[Callable] = None,
            on_focus_in: Optional[Callable] = None,
            on_focus_out: Optional[Callable] = None,

            width: int = 140,
            height: int = 28,

            state: str = tkinter.NORMAL,

            hide_on_focus_out: bool = False,
            **kwargs
    ):
        super().__init__(master, fg_color="transparent")

        self.on_text_changed = on_text_changed if on_text_changed is not None else lambda: None
        self.on_focus_in = on_focus_in if on_focus_in is not None else lambda: None
        self.on_focus_out = on_focus_out if on_focus_out is not None else lambda: None

        self.label = customtkinter.CTkLabel(
            self,
            text=label_text,
        )
        self.label.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        self.entry = customtkinter.CTkEntry(
            self,
            state=state,
            textvariable=textvariable,
            width=width,
            height=height,

            **kwargs
        )

        if state == tkinter.DISABLED:
            self.entry.configure(fg_color="gray25", border_color="gray25")

        self.entry.grid(row=1, column=0, padx=0, pady=0, sticky="w")
        self.entry.bind("<KeyRelease>", self.text_changed)

        self.text = textvariable.get().strip() if isinstance(textvariable, tkinter.StringVar) else ""
        self.is_shortened = False
        if hide_on_focus_out:
            shortened_string = gui_utils.shorten_long_string(self.text)
            self.entry.configure(textvariable=tkinter.StringVar(value=shortened_string))
            self.is_shortened = True

            self.entry.bind("<FocusIn>", self.focus_in)
            self.entry.bind("<FocusOut>", self.focus_out)

    def get(self):
        return self.entry.get().strip()

    def bind(self, sequence, command, add=True):
        self.entry.bind(sequence, command, add)

    def show_full_text(self):
        self.entry.configure(textvariable=tkinter.StringVar(value=self.text))
        self.is_shortened = False

    def hide_full_text(self):
        text = gui_utils.shorten_long_string(self.text)
        self.entry.configure(textvariable=tkinter.StringVar(value=text))
        self.is_shortened = True

    def text_changed(self, event):
        self.text = self.entry.get().strip()

        self.on_text_changed()

    def focus_in(self, event):
        self.on_focus_in()

        self.show_full_text()

    def focus_out(self, event):
        self.on_focus_out()

        self.hide_full_text()

    def set_text_changed_callback(self, callback: Callable):
        self.entry.bind("<KeyRelease>", lambda event: callback())

    def set_click_callback(self, callback: Callable):
        self.entry.bind("<Button-1>", lambda event: callback())

    def set_focus_in_callback(self, callback: Callable):
        self.on_focus_in = callback

    def set_focus_out_callback(self, callback: Callable):
        self.on_focus_out = callback
