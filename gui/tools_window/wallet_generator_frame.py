from tkinter import filedialog
from tkinter import messagebox

import customtkinter

from gui.objects import FloatSpinbox
from utils.key_manager.generator import Generator
from utils.file_manager import FileManager


class WalletGeneratorFrame(customtkinter.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=0)

        self.label = customtkinter.CTkLabel(
            master=self,
            text="Generate wallets (private keys)",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, sticky="wn", pady=10, padx=15)

        self.amount_label = customtkinter.CTkLabel(
            master=self, text="Amount:", font=customtkinter.CTkFont(size=12)
        )
        self.amount_label.grid(row=1, column=0, sticky="w", pady=(0, 0), padx=15)

        self.amount_spinbox = FloatSpinbox(
            master=self,
            step_size=5,
            max_value=500,
            start_index=5,
        )
        self.amount_spinbox.grid(row=2, column=0, sticky="w", pady=(0, 10), padx=15)

        self.generate_button = customtkinter.CTkButton(
            master=self,
            text="Save to file",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            command=self.generate_button_event,
        )
        self.generate_button.grid(row=3, column=0, sticky="w", pady=15, padx=15)

    def generate_button_event(self):
        amount = int(self.amount_spinbox.get())
        if not amount:
            messagebox.showerror(
                title="Error",
                message="Amount must be greater than 0"
            )
            return

        wallets = Generator.generate_keys(amount)

        file_path = filedialog.asksaveasfilename(
            title="Save wallets",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"),),
            initialfile=f"generated_apt.txt"
        )

        FileManager.write_data_to_txt_file(file_path=file_path, data=wallets)
