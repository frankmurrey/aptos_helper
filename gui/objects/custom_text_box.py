import customtkinter


class CTkCustomTextBox(customtkinter.CTkTextbox):
    def __init__(
            self,
            master,
            grid: dict,
            text: str,
            height: int = 100,
            font: tuple = ("Consolas", 14),
    ):
        super().__init__(master=master, font=font, fg_color='gray14')
        self.configure(height=height)
        self.grid(**grid)
        self.insert("1.0", text)
