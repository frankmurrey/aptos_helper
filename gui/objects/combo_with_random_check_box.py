import random
from typing import Optional, Callable

import customtkinter


class ComboWithRandomCheckBox:
    def __init__(
            self,
            master,
            grid: dict,
            options: list,
            text: str = "Random",
            combo_command: Optional[Callable] = lambda _: None,
    ):
        self.options = options

        self.combobox = customtkinter.CTkComboBox(
            master=master,
            values=options,
            width=130,
            command=combo_command
        )
        self.combobox.grid(**grid)

        self.random_checkbox = customtkinter.CTkCheckBox(
            master=master,
            text=text,
            checkbox_width=18,
            checkbox_height=18,
            onvalue=True,
            offvalue=False,
            command=self.random_checkbox_event,
        )
        self.random_checkbox.grid(row=grid["row"] + 1, column=grid["column"], padx=20, pady=5, sticky="w")

    def random_checkbox_event(self):
        if self.random_checkbox.get():
            self.combobox.configure(
                state="disabled",
                fg_color='#3f3f3f',
            )
        else:
            self.combobox.configure(
                state="normal",
                fg_color='#343638',
            )

    def get_value(self):
        if self.random_checkbox.get():
            return random.choice(self.options)
        return self.combobox.get()

    def get_checkbox_value(self):
        return self.random_checkbox.get()

    def set_values(self, combo_value: str):

        if combo_value.lower() == 'random':
            self.combobox.configure(
                state="disabled",
                fg_color='#3f3f3f',
            )
            self.random_checkbox.select()
        else:
            self.combobox.configure(
                state="normal",
                fg_color='#343638',
            )
            self.combobox.set(combo_value)
            self.random_checkbox.deselect()