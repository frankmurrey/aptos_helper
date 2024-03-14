from typing import Callable, Union

import customtkinter
from PIL import Image, ImageEnhance


class IconButton(customtkinter.CTkButton):
    def __init__(
            self,
            master,
            icon: Union[str, Image.Image],
            dark_icon: Union[str, Image.Image] = None,
            command: Callable[[], None] = lambda: None,

            text: str = "",
            text_color: str = "grey",
            size: tuple[int, int] = (20, 20),


            width: int = 5,
    ):

        if isinstance(icon, str):
            icon = Image.open(icon)
        self.icon = icon

        if dark_icon is not None:
            if isinstance(dark_icon, str):
                dark_icon = Image.open(dark_icon)
            self.dark_icon = dark_icon
        else:
            self.dark_icon = self.icon

        enhancer = ImageEnhance.Brightness(self.icon)
        self.hover_icon = enhancer.enhance(0.75)

        enhancer = ImageEnhance.Brightness(self.dark_icon)
        self.hover_dark_icon = enhancer.enhance(0.75)

        self.ctk_icon = customtkinter.CTkImage(
            light_image=self.icon,
            dark_image=self.dark_icon,
            size=size
        )

        self.ctk_icon_hover = customtkinter.CTkImage(
            light_image=self.hover_icon,
            dark_image=self.hover_dark_icon,
            size=size
        )

        super().__init__(
            master,
            text=text,
            text_color=text_color,
            bg_color="transparent",
            fg_color="transparent",
            image=self.ctk_icon,
            hover=False,
            command=command,
            width=width
        )

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.configure(image=self.ctk_icon_hover)

    def on_leave(self, event):
        self.configure(image=self.ctk_icon)


if __name__ == '__main__':
    import tkinter
    from PIL import Image

    root = tkinter.Tk()
    root.geometry("200x200")

    icon = Image.open(r"D:\dev\frankmurrey\starknet_drop_helper\gui\images\edit_button.png")
    button = IconButton(master=root, icon=icon, command=lambda: print("test"))
    button.grid(row=0, column=0)

    root.mainloop()
