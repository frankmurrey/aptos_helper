import customtkinter

from src.utils.generate_wallets import generate_keys

from tkinter import (messagebox,
                     filedialog)


class ToolsTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x600")

        self.generator_label = customtkinter.CTkLabel(self,
                                                      text="Generate aptos keys to file:",
                                                      font=customtkinter.CTkFont(size=14, weight="bold"))
        self.generator_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.wallet_generator_frame = customtkinter.CTkFrame(master=self)
        self.wallet_generator_frame.rowconfigure((1, 2, 3), weight=0)
        self.wallet_generator_frame.rowconfigure((0, 4), weight=1)
        self.wallet_generator_frame.grid(row=1, rowspan=4, column=0, padx=15, sticky="wns")

        self.wallet_amount_to_generate_label = customtkinter.CTkLabel(self.wallet_generator_frame,
                                                                      text="Amount:")
        self.wallet_amount_to_generate_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.wallet_amount_to_generate_entry = customtkinter.CTkEntry(self.wallet_generator_frame,
                                                                      width=70)
        self.wallet_amount_to_generate_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.generate_aptos_wallets_button = customtkinter.CTkButton(self.wallet_generator_frame,
                                                                     text="Generate",
                                                                     width=70,
                                                                     command=self.generate_button_event)
        self.generate_aptos_wallets_button.grid(row=0, column=2, padx=10, pady=10, sticky="w")

    def generate_button_event(self):
        amount = self.wallet_amount_to_generate_entry.get()
        if not amount:
            messagebox.showerror("Error", "Amount cannot be empty")
            return
        try:
            amount = int(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        if amount < 1:
            messagebox.showerror("Error", "Amount must be greater than 0")
            return

        keys = generate_keys(amount)

        self.save_keys(keys)

    def save_keys(self, keys):
        file_path = filedialog.asksaveasfilename(title="Save keys",
                                                 defaultextension=".txt",
                                                 filetypes=(("Text files", "*.txt"),),
                                                 initialfile=f"aptos_k.txt")
        if not file_path:
            return

        with open(file_path, "w") as f:
            f.write("\n".join(keys))

        messagebox.showinfo("Success", "Keys saved to {}".format(file_path))
