import customtkinter

from src import enums
from gui.objects import FloatSpinbox


class ModuleSelectFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            action: dict = None,
    ):
        super().__init__(master=master)
        self.master = master
        self.action = action

        self.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="nsew"

        )
        self.label = customtkinter.CTkLabel(
            self,
            text="Module:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.modules_option_menu = customtkinter.CTkOptionMenu(
            self,
            values=self.tab_names,
            command=master.set_new_tab
        )
        self.modules_option_menu.grid(
            row=1,
            column=0,
            padx=20,
            pady=(5, 20),
            sticky="w"
        )

        self.actions_amount_label = customtkinter.CTkLabel(
            self,
            text="Repeats:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.actions_amount_label.grid(
            row=0,
            column=1,
            padx=20,
            pady=(5, 0),
            sticky="w"
        )

        self.float_spinbox = FloatSpinbox(master=self, max_value=100)
        self.float_spinbox.grid(
            row=1,
            column=1,
            padx=20,
            pady=(5, 20),
            sticky="w"
        )

        self.probability_label = customtkinter.CTkLabel(
            self,
            text="Probability %:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.probability_label.grid(
            row=0,
            column=2,
            padx=(10, 20),
            pady=(5, 0),
            sticky="w"
        )

        self.probability_spinbox = FloatSpinbox(master=self, max_value=100, start_index=100)
        self.probability_spinbox.grid(
            row=1,
            column=2,
            padx=(10, 20),
            pady=(5, 20),
            sticky="w"
        )

    @property
    def tab_names(self) -> list:
        if self.action:
            values = [self.action["tab_name"]]
        else:
            tab: enums.TabName
            values = [tab.value for tab in enums.TabName]

        return values
