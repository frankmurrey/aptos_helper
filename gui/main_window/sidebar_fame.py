import customtkinter
import webbrowser

from src import paths
from gui.tools_window.top_level import ToolsWindow
from gui.settings_window.top_level import SettingsWindow

from PIL import Image


class SidebarFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs):

        super().__init__(master, **kwargs)
        self.master = master

        self.tools_window = None
        self.settings_window = None
        self.right_frame = master.right_frame

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)
        self.grid_rowconfigure(9, weight=1)
        self.grid(
            row=0,
            column=0,
            sticky="nsw"
        )
        self.tabview = customtkinter.CTkTabview(
            self,
            width=400,
            height=840,
            bg_color="transparent"
        )
        logo_image = customtkinter.CTkImage(
            light_image=Image.open(paths.LIGHT_MODE_LOGO_IMG),
            dark_image=Image.open(paths.DARK_MODE_LOGO_IMG),
            size=(150, 90)
        )
        self.logo_label = customtkinter.CTkLabel(
            self,
            image=logo_image,
            text=""
        )
        self.logo_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10)
        )
        self.tools_button = customtkinter.CTkButton(
            self,
            text="Tools",
            command=self.tools_button_event,
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.tools_button.grid(
            row=1,
            column=0,
            padx=25,
            pady=(10, 20),
            sticky="w"
        )

        self.settings_button = customtkinter.CTkButton(
            self,
            text="Settings",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.settings_button_event
        )
        self.settings_button.grid(
            row=2,
            column=0,
            padx=25,
            pady=(0, 20),
            sticky="w"
        )

        self.appearance_mode_label = customtkinter.CTkLabel(
            self,
            text="Appearance Mode:",
            anchor="w")
        self.appearance_mode_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 80),
            sticky="s"
        )
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 50),
            sticky="s"
        )

        link_font = customtkinter.CTkFont(
            size=12,
            underline=True
        )
        self.github_button = customtkinter.CTkButton(
            self,
            text="v2.1.0 Github origin",
            font=link_font,
            width=140,
            anchor="c",
            text_color="grey",
            fg_color='transparent',
            hover=False,
            command=self.open_github
        )
        self.github_button.grid(
            row=9,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="s"
        )

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def open_github(self):
        webbrowser.open("https://github.com/frankmurrey/aptos_drop_helper")

    def add_new_module_tab(
            self,
            module_name: str
    ):
        """
        Add new module tab to the tabview
        :param module_name: tab name
        :return: 
        """
        self.master.modules_frame.tabview.add(module_name.title())
        self.master.modules_frame.tabview.set(module_name.title())

    def tools_button_event(self):
        geometry = "450x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "450x600+1050+100"

        if self.tools_window is None or not self.tools_window.winfo_exists():
            self.tools_window = ToolsWindow(self)
            self.tools_window.geometry(geometry)
            self.tools_window.resizable(False, False)
        else:
            self.tools_window.focus()

    def settings_button_event(self):
        geometry = "450x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "450x600+1050+100"

        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
            self.settings_window.geometry(geometry)
            self.settings_window.resizable(False, False)
        else:
            self.settings_window.focus()



