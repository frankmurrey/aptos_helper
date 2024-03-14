import customtkinter

from gui.settings_window.app_config_frame import AppConfigFrame


class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Settings")
        self.after(10, self.focus_force)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.master = master

        self.app_config_frame = AppConfigFrame(master=self)
