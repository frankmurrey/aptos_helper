import customtkinter

from tkinter import messagebox, filedialog

from gui.swaps_window import SwapsModule
from gui.aptos_bridge_window import AptosBridgeModule
from gui.abel_finance_window import AbleFinanceWindow
from gui.liquidity_window import Liquidity
from gui.tools_window import ToolsTopLevelWindow

from src.file_manager import FileManager
from src.storage import WalletsStorage
from src.paths import (DARK_MODE_LOGO_IMG,
                       LIGHT_MODE_LOGO_IMG,
                       TOOLS_LOGO)

from PIL import Image


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aptos Helper by @frankmurrey")
        self.geometry(f"{700}x{900}")

        self.grid_columnconfigure(8, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.wallets_storage = WalletsStorage()
        self.wallets_data = self.wallets_storage.get_wallets_data()

        if self.wallets_data is None:
            self.aptos_wallets_data = []
            self.evm_addresses_data = []
            self.proxy_data = []
        else:
            self.aptos_wallets_data = [wallet.wallet for wallet in self.wallets_data if wallet.wallet]
            self.proxy_data = [wallet.proxy for wallet in self.wallets_data if wallet.proxy]
            self.evm_addresses_data = [wallet.evm_pair_address for wallet in self.wallets_data if wallet.evm_pair_address]

        self.tools_window = None

        self.sidebar_frame = customtkinter.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        logo_image = customtkinter.CTkImage(light_image=Image.open(LIGHT_MODE_LOGO_IMG),
                                            dark_image=Image.open(DARK_MODE_LOGO_IMG),
                                            size=(150, 85))

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 image=logo_image,
                                                 text="")
        self.tabview = customtkinter.CTkTabview(self, width=400, height=840, bg_color="transparent")

        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_swap_button = customtkinter.CTkButton(self.sidebar_frame,
                                                           text="Swap",
                                                           command=self.add_swaps_tabview)

        self.sidebar_swap_button.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_liquidity_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                text="Liquidity",
                                                                command=self.add_liquidity_tabview)
        self.sidebar_liquidity_button.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_aptos_bridge_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                   text="Aptos Bridge",
                                                                   command=self.add_aptos_bridge_tabview)
        self.sidebar_aptos_bridge_button.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_abel_finance_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                   text="Abel finance",
                                                                   command=self.add_abel_finance_tabview)
        self.sidebar_abel_finance_button.grid(row=4, column=0, padx=20, pady=10)

        tools_logo_img = customtkinter.CTkImage(light_image=Image.open(TOOLS_LOGO),
                                                size=(20, 20))
        self.tools_button = customtkinter.CTkButton(self.sidebar_frame,
                                                    image=tools_logo_img,
                                                    fg_color="#BE5504",
                                                    text="Tools",
                                                    hover_color="#80400B",
                                                    anchor="c",
                                                    command=self.open_tools_window)
        self.tools_button.grid(row=5, column=0, padx=20, pady=10)

        self.wallets_loaded_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                           text="Wallets Loaded:",
                                                           anchor="w",
                                                           font=customtkinter.CTkFont(size=16, weight="bold"))
        self.wallets_loaded_label.grid(row=6, column=0, padx=20, pady=(0, 0))

        self.load_aptos_wallets_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                 text="+",
                                                                 width=20,
                                                                 height=20,
                                                                 anchor="c",
                                                                 corner_radius=200,
                                                                 command=self.load_aptos_wallets_from_file)
        self.load_aptos_wallets_button.grid(row=6, column=0, padx=(0, 118), pady=(70, 0))

        self.aptos_wallet_load_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                              text=f"Aptos: ",
                                                              anchor="w",
                                                              bg_color="transparent",
                                                              font=customtkinter.CTkFont(size=14, weight="bold"))
        self.aptos_wallet_load_label.grid(row=6, column=0, padx=(0, 15), pady=(70, 0))
        self.aptos_loaded_wallet_num_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                                    text=f"{len(self.aptos_wallets_data)}",
                                                                    justify="right",
                                                                    font=customtkinter.CTkFont(size=16, weight="bold")
                                                                    )
        self.aptos_loaded_wallet_num_label.grid(row=6, column=0, padx=(70, 0), pady=(70, 0))

        self.load_evm_addresses_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                 text="+",
                                                                 width=20,
                                                                 height=20,
                                                                 anchor="c",
                                                                 corner_radius=200,
                                                                 command=self.load_evm_addresses_from_file)
        self.load_evm_addresses_button.grid(row=6, column=0, padx=(0, 118), pady=(140, 0))

        self.evm_addresses_load_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                               text=f"EVM: ",
                                                               anchor="e",
                                                               bg_color="transparent",
                                                               font=customtkinter.CTkFont(size=14, weight="bold"))
        self.evm_addresses_load_label.grid(row=6, column=0, padx=(0, 25), pady=(140, 0))
        self.evm_addresses_loaded_num_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                                     text=f"{len(self.evm_addresses_data)}",
                                                                     anchor="e",
                                                                     bg_color="transparent",
                                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
        self.evm_addresses_loaded_num_label.grid(row=6, column=0, padx=(70, 0), pady=(140, 0))

        self.load_proxy_button = customtkinter.CTkButton(self.sidebar_frame,
                                                         text="+",
                                                         width=20,
                                                         height=20,
                                                         anchor="c",
                                                         corner_radius=200,
                                                         command=self.load_proxy_from_file)

        self.load_proxy_button.grid(row=6, column=0, padx=(0, 118), pady=(210, 0))

        self.proxy_load_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                       text=f"Proxy: ",
                                                       anchor="e",
                                                       bg_color="transparent",
                                                       font=customtkinter.CTkFont(size=14, weight="bold"))
        self.proxy_load_label.grid(row=6, column=0, padx=(0, 18), pady=(210, 0))
        self.proxy_loaded_num_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                             text=f"{len(self.proxy_data)}",
                                                             anchor="e",
                                                             bg_color="transparent",
                                                             font=customtkinter.CTkFont(size=16, weight="bold"))
        self.proxy_loaded_num_label.grid(row=6, column=0, padx=(70, 0), pady=(210, 0))

        self.shuffle_wallets_switch = customtkinter.CTkSwitch(self.sidebar_frame,
                                                              text="Shuffle wallets",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color="#F47174",
                                                              onvalue=True,
                                                              offvalue=False,
                                                              command=self.shuffle_wallets_event)
        self.shuffle_wallets_switch.grid(row=6, column=0, padx=(0, 10), pady=(270, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(0, 55))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(0, 0))

    def open_tools_window(self):
        if self.tools_window is None or not self.tools_window.winfo_exists():
            self.tools_window = ToolsTopLevelWindow(self)
            self.tools_window.title("Tools")
        else:
            self.tools_window.focus()

    def add_swaps_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Swap")
            self.tabview.tab("Swap").grid_columnconfigure(0, weight=3)

            swaps = SwapsModule(tabview=self.tabview)
            swaps.add_all_fields()
        except Exception as e:
            pass

    def add_aptos_bridge_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Aptos Bridge")
            self.tabview.tab("Aptos Bridge").grid_columnconfigure(1, weight=3)

            bridge = AptosBridgeModule(tabview=self.tabview)
            bridge.add_all_fields()
        except Exception as e:
            pass

    def add_abel_finance_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Abel finance")
            self.tabview.tab("Abel finance").grid_columnconfigure(0, weight=3)

            abel_finance = AbleFinanceWindow(tabview=self.tabview)
            abel_finance.add_all_fields()
        except Exception as e:
            pass

    def add_liquidity_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Liquidity")
            self.tabview.tab("Liquidity").grid_columnconfigure(0, weight=3)

            liquidity = Liquidity(tabview=self.tabview)
            liquidity.add_all_fields()
        except Exception as e:
            pass

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def shuffle_wallets_event(self):
        status = self.shuffle_wallets_switch.get()
        self.wallets_storage.set_shuffle_wallets(status)
        if status:
            self.shuffle_wallets_switch.configure(text_color="#6fc276")
        else:
            self.shuffle_wallets_switch.configure(text_color="#F47174")

    @property
    def amount_of_loaded_aptos_wallets(self):
        if not self.wallets_data:
            return 0

        aptos_wallets = [wallet.wallet for wallet in self.wallets_data]
        return len(aptos_wallets)

    @property
    def amount_of_loaded_evm_addresses(self):
        if not self.wallets_data:
            return 0

        evm_addresses = []
        for wallet_data in self.wallets_data:
            if wallet_data.evm_pair_address is None:
                continue

            evm_addresses.append(wallet_data.evm_pair_address)

        return len(evm_addresses)

    @property
    def amount_of_loaded_proxy(self):
        if not self.wallets_data:
            return 0

        proxy = []
        for wallet_data in self.wallets_data:
            if wallet_data.proxy is None:
                continue
            proxy.append(wallet_data.proxy)

        return len(proxy)

    def update_wallets_loaded_label(self):
        self.aptos_loaded_wallet_num_label.configure(text=f"{self.amount_of_loaded_aptos_wallets}")
        self.evm_addresses_loaded_num_label.configure(text=f"{self.amount_of_loaded_evm_addresses}")
        self.proxy_loaded_num_label.configure(text=f"{self.amount_of_loaded_proxy}")

    def load_wallets_from_storage(self):
        self.aptos_wallets_data = [wallet.wallet for wallet in self.wallets_data if wallet.wallet]
        self.evm_addresses_data = [wallet.evm_pair_address for wallet in self.wallets_data if wallet.evm_pair_address]
        self.update_wallets_loaded_label()

    def load_aptos_wallets_from_file(self):
        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select aptos wallets file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        if not file_path:
            return

        try:
            data = FileManager().read_data_from_txt_file(file_path)
            self.aptos_wallets_data = data
            self.wallets_data = FileManager().get_wallets(aptos_wallets_data=data)
            self.wallets_storage.set_wallets_data(self.wallets_data)
            self.update_wallets_loaded_label()

        except Exception as e:
            messagebox.showerror("Error", f"Wrong data format in file: {e}")

    def load_evm_addresses_from_file(self):
        if not self.aptos_wallets_data:
            messagebox.showerror("Error", "Load aptos wallets first")
            return

        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select evm addresses file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        if not file_path:
            return

        try:
            data = FileManager().read_data_from_txt_file(file_path)
            self.evm_addresses_data = data
            self.wallets_data = FileManager().get_wallets(aptos_wallets_data=self.aptos_wallets_data,
                                                          evm_addresses_data=data)
            self.wallets_storage.set_wallets_data(self.wallets_data)
            self.update_wallets_loaded_label()

        except Exception as e:
            messagebox.showerror("Error", f"Wrong data format in file: {e}")

    def load_proxy_from_file(self):
        if not self.aptos_wallets_data:
            messagebox.showerror("Error", "Load aptos wallets first")
            return

        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select proxy file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        if not file_path:
            return

        try:
            data = FileManager().read_data_from_txt_file(file_path)
            self.proxy_data = data
            self.wallets_data = FileManager().get_wallets(aptos_wallets_data=self.aptos_wallets_data,
                                                          evm_addresses_data=self.evm_addresses_data,
                                                          proxy_data=data)
            self.wallets_storage.set_wallets_data(self.wallets_data)
            self.update_wallets_loaded_label()

        except Exception as e:
            messagebox.showerror("Error", f"Wrong data format in file: {e}")