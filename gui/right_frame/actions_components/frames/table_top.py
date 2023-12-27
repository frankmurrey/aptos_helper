import customtkinter


class TableTopFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 0),
            sticky="nsew"
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="uniform")
        self.grid_columnconfigure(4, weight=1)

        self.action_name_label = customtkinter.CTkLabel(
            self,
            text="Module",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_name_label.grid(
            row=0,
            column=0,
            padx=(60, 30),
            pady=0
        )

        self.action_type_label = customtkinter.CTkLabel(
            self,
            text="Action",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.action_type_label.grid(
            row=0,
            column=1,
            padx=10,
            pady=0
        )

        self.repeats_label = customtkinter.CTkLabel(
            self,
            text="Info",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(
            row=0,
            column=2,
            padx=5,
            pady=0
        )

        self.action_info_label = customtkinter.CTkLabel(
            self,
            text="Repeats",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_info_label.grid(
            row=0,
            column=3,
            padx=(0, 0),
            pady=0
        )

        self.buttons_label = customtkinter.CTkLabel(
            self,
            text="   ",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.buttons_label.grid(
            row=0,
            column=4,
            padx=(60, 40),
            pady=0
        )
