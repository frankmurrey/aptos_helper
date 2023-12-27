import customtkinter
from typing import Optional

from src.repr.event_manager import repr_event_manager
from src.repr.repr_manager import repr_manager
from src.tasks_executor import task_executor
from src.logger import configure_logger
from PIL import Image

import pystray
from pystray import MenuItem

from src.paths import GUI_DIR
from gui.main_window.sidebar_fame import SidebarFrame
from gui.right_frame.main_frame import RightFrame


from src.templates.templates import Templates


def run_gui():
    window = MainWindow()
    try:
        window.mainloop()
    except KeyboardInterrupt:
        window.on_closing()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.on_start()

        self.resizable(False, False)
        if self.winfo_screenheight() < 950:
            self.resizable(False, True)

        self.title("Aptos Helper by @frankmurrey")

        self.geometry(f"{1490}x{900}+100+100")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        self.right_frame = RightFrame(self)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.tray_icon: Optional["pystray.Icon"] = None

    def create_image(self, width, height, color1, color2):
        image = Image.open(f"{GUI_DIR}/images/tray_icon.png")
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        return image

    def init_tray_icon(self):
        icon_image = self.create_image(64, 64, 'black', 'red')

        menu = (
            MenuItem('Show', self.show_window, default=True),
            MenuItem('Quit', self.quit_window)
        )

        self.tray_icon = pystray.Icon("tray_icon", icon_image, "StarkNet Helper", menu)
        self.tray_icon.run_detached()

    def hide_window(self):
        self.withdraw()

    def show_window(self, icon, item):
        self.deiconify()

    def quit_window(self, icon, item):
        icon.visible = False
        icon.stop()
        self.on_closing()

    def on_start(self):
        configure_logger()
        repr_manager.print_logo_message()
        Templates().create_not_found_temp_files()
        repr_event_manager.start()
        self.init_tray_icon()

    def on_closing(self):
        task_executor.stop()
        self.quit()