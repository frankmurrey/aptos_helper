import customtkinter


class StatusInfoWindow(customtkinter.CTkToplevel):
    def __init__(self, master, info: str):
        super().__init__(master)

        self.master = master
        self.info = info

        self.title("Status Info")
        self.geometry("600x400")

        self.after(10, self.focus_force)
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.close)

        # INFO FRAME
        self.info_frame = customtkinter.CTkFrame(
            self,
            bg_color="grey20",
            fg_color="grey20",
        )
        self.info_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10,
        )

        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(0, weight=1)

        # INFO TEXT
        self.info_text_box = customtkinter.CTkTextbox(
            self,
            activate_scrollbars=True,
        )
        self.info_text_box.insert("end", self.info)
        self.info_text_box.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10,
        )

    def close(self):
        self.info_frame.destroy()
        self.destroy()
