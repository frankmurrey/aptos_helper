import yaml

import customtkinter

from tkinter import messagebox, filedialog

from gui.pancake_window import PancakeModule
from gui.aptos_bridge_window import AptosBridgeModule
from gui.abel_finance_window import AbleFinanceWindow
from gui.thala_window import ThalaWindow

from src.file_manager import FileManager
from src.storage import WalletsStorage


customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


def run_gui():
    window = MainWindow()
    window.mainloop()


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aptos helper by @frankmurrey")
        self.geometry(f"{600}x{750}")

        self.grid_columnconfigure(8, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.wallets_data = FileManager().get_wallets()
        self.wallets_storage = WalletsStorage()

        if self.wallets_data is None:
            self.aptos_wallets_data = []
            self.evm_addresses_data = []
        else:
            self.aptos_wallets_data = [wallet.wallet for wallet in self.wallets_data if wallet.wallet]
            self.evm_addresses_data = [wallet.evm_pair_address for wallet in self.wallets_data if wallet.evm_pair_address]

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 text="Aptos Helper",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"),
                                                 )
        self.tabview = customtkinter.CTkTabview(self, width=350, height=700, bg_color="transparent")

        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_pancake_button = customtkinter.CTkButton(self.sidebar_frame,
                                                              text="Pancake Swap",
                                                              command=self.add_pancake_tabview)

        self.sidebar_pancake_button.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_aptos_bridge_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                   text="Aptos Bridge",
                                                                   command=self.add_aptos_bridge_tabview)
        self.sidebar_aptos_bridge_button.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_abel_finance_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                   text="Abel finance",
                                                                   command=self.add_abel_finance_tabview)
        self.sidebar_abel_finance_button.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_thala_button = customtkinter.CTkButton(self.sidebar_frame,
                                                            text="Thala",
                                                            command=self.add_thala_tabview)
        self.sidebar_thala_button.grid(row=4, column=0, padx=20, pady=10)

        self.wallets_loaded_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                           text="Wallets Loaded:",
                                                           anchor="w",
                                                           font=customtkinter.CTkFont(size=16, weight="bold"))
        self.wallets_loaded_label.grid(row=6, column=0, padx=20, pady=(0, 0))

        self.load_aptos_wallets_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                 text="+",
                                                                 width=25,
                                                                 height=25,
                                                                 anchor="c",
                                                                 command=self.load_aptos_wallets_from_file)
        self.load_aptos_wallets_button.grid(row=6, column=0, padx=(0, 118), pady=(70, 0))

        self.aptos_wallet_load_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                              text=f"Aptos: {self.amount_of_loaded_aptos_wallets}",
                                                              anchor="e",
                                                              bg_color="transparent",
                                                              font=customtkinter.CTkFont(size=14, weight="bold"))
        self.aptos_wallet_load_label.grid(row=6, column=0, padx=(0, 15), pady=(70, 0))

        self.load_evm_addresses_button = customtkinter.CTkButton(self.sidebar_frame,
                                                                 text="+",
                                                                 width=25,
                                                                 height=25,
                                                                 anchor="c",
                                                                 command=self.load_evm_addresses_from_file)
        self.load_evm_addresses_button.grid(row=6, column=0, padx=(0, 118), pady=(140, 0))

        self.evm_addresses_load_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                               text=f"EVM: {self.amount_of_loaded_evm_addresses}",
                                                               anchor="e",
                                                               bg_color="transparent",
                                                               font=customtkinter.CTkFont(size=14, weight="bold"))
        self.evm_addresses_load_label.grid(row=6, column=0, padx=(0, 25), pady=(140, 0))
        self.shuffle_wallets_switch = customtkinter.CTkSwitch(self.sidebar_frame,
                                                              text="Shuffle wallets",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color="#F47174",
                                                              onvalue=True,
                                                              offvalue=False,
                                                              command=self.shuffle_wallets_event)
        self.shuffle_wallets_switch.grid(row=6, column=0, padx=(0, 10), pady=(200, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(0, 55))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(0, 0))

    def add_pancake_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Pancake")
            self.tabview.tab("Pancake").grid_columnconfigure(0, weight=3)

            cake = PancakeModule(tabview=self.tabview)
            cake.add_all_fields()

        except Exception as e:
            print(e)
            pass

    def add_aptos_bridge_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Aptos Bridge")
            self.tabview.tab("Aptos Bridge").grid_columnconfigure(1, weight=3)

            bridge = AptosBridgeModule(tabview=self.tabview)
            bridge.add_all_fields()
        except Exception as e:
            print(e)
            pass

    def add_abel_finance_tabview(self):
        try:
            self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
            self.tabview.add("Abel finance")
            self.tabview.tab("Abel finance").grid_columnconfigure(0, weight=3)

            abel_finance = AbleFinanceWindow(tabview=self.tabview)
            abel_finance.add_all_fields()
        except Exception as e:
            print(e)
            pass

    def add_thala_tabview(self):
        self.tabview.grid(row=0, column=1, padx=(20, 0), pady=(0, 0))
        self.tabview.add("Thala")
        self.tabview.tab("Thala").grid_columnconfigure(0, weight=3)

        thala = ThalaWindow(tabview=self.tabview)
        thala.add_all_fields()

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

        aptos_wallets = [wallet.wallet for wallet in self.wallets_data if len(wallet.wallet) == 66]
        return len(aptos_wallets)

    @property
    def amount_of_loaded_evm_addresses(self):
        if not self.wallets_data:
            return 0

        evm_addresses = []
        for wallet_data in self.wallets_data:
            if wallet_data.evm_pair_address is None:
                continue

            if len(wallet_data.evm_pair_address) == 42:
                evm_addresses.append(wallet_data.evm_pair_address)

        return len(evm_addresses)

    def update_wallets_loaded_label(self):
        self.aptos_wallet_load_label.configure(text=f"Aptos: {self.amount_of_loaded_aptos_wallets}")
        self.evm_addresses_load_label.configure(text=f"EVM: {self.amount_of_loaded_evm_addresses}")

    def load_wallets_from_storage(self):
        self.aptos_wallets_data = [wallet.wallet for wallet in self.wallets_data if wallet.wallet]
        self.evm_addresses_data = [wallet.evm_pair_address for wallet in self.wallets_data if wallet.evm_pair_address]
        self.update_wallets_loaded_label()

    def load_aptos_wallets_from_file(self):
        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select wallet file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        if file_path == "":
            return
        try:
            data = FileManager().read_data_from_txt_file(file_path)
            self.aptos_wallets_data = data
            self.wallets_data = FileManager().get_wallets(aptos_wallets_file_data=data)
            self.wallets_storage.set_wallets_data(self.wallets_data)
            self.update_wallets_loaded_label()

        except Exception as e:
            messagebox.showerror("Error", f"Wrong data format in file: {e}")

    def load_evm_addresses_from_file(self):
        if not self.aptos_wallets_data:
            messagebox.showerror("Error", "Load aptos wallets first")
            return

        file_path = filedialog.askopenfilename(initialdir=".",
                                               title="Select wallet file",
                                               filetypes=(("Text files", "*.txt"), ("all files", "*.*")))

        if file_path == "":
            return

        try:
            data = FileManager().read_data_from_txt_file(file_path)
            self.evm_addresses_data = data
            self.wallets_data = FileManager().get_wallets(evm_addresses_file_data=data,
                                                          aptos_wallets_file_data=self.aptos_wallets_data)
            self.wallets_storage.set_wallets_data(self.wallets_data)
            self.update_wallets_loaded_label()
        except Exception as e:
            messagebox.showerror("Error", f"Wrong data format in file: {e}")
