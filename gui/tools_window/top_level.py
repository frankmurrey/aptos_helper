import customtkinter

from gui.right_frame.main_frame import RightFrame
from gui.tools_window.balance_checker_frame import BalanceCheckerFrame
from gui.tools_window.wallet_generator_frame import WalletGeneratorFrame


class ToolsWindow(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Tools")
        self.after(10, self.focus_force)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.master = master
        self.right_frame: RightFrame = master.right_frame

        self.wallet_generator_frame = WalletGeneratorFrame(master=self)
        self.balance_checker_frame = BalanceCheckerFrame(
            master=self,
            right_frame=self.right_frame
        )
