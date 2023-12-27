import webbrowser

import customtkinter
import gui.constants as constants


class LinkButton(customtkinter.CTkButton):
    def __init__(
            self,
            master,
            link: str,
            grid: dict,

            label_text: str = "Link (click)",
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.master = master
        self.link = link

        self.configure(
            text=label_text,
            fg_color='transparent',
            bg_color='transparent',
            hover=False,
            command=self.open_link,
            font=customtkinter.CTkFont(size=12, weight="bold", underline=True),
            text_color=constants.LINK_COLOR_HEX
        )

        self.grid(**grid)

    def open_link(self):
        webbrowser.open(self.link)