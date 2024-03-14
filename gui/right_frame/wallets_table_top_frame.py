import customtkinter


class WalletsTableTop(customtkinter.CTkFrame):
    def __init__(self,
                 master,
                 grid,
                 wallet_items: list):
        super().__init__(master)

        self.master = master
        self.wallet_items = wallet_items
        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(**grid)

        self.frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform='a')

        self.chose_all_checkbox = customtkinter.CTkCheckBox(
            self.frame,
            text="",
            checkbox_width=20,
            checkbox_height=20,
            onvalue=True,
            offvalue=False,
            command=self.select_all_checkbox_event
        )

        pad_x = (50, 0)
        pad_y = 5

        self.chose_all_checkbox.grid(
            row=0,
            column=0,
            padx=25,
            pady=5,
            sticky="w"
        )

        self.wallet_name_label = customtkinter.CTkLabel(
            self.frame,
            text="Name",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.wallet_name_label.grid(
            row=0,
            column=0,
            padx=(75, 0),
            pady=pad_y,
            sticky="w"
        )

        self.wallet_address_label = customtkinter.CTkLabel(
            self.frame,
            text="Address",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_address_label.grid(
            row=0,
            column=1,
            padx=(70, 0),
            pady=pad_y,
            sticky="w"
        )

        self.pair_address_label = customtkinter.CTkLabel(
            self.frame,
            text="Pair Address",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.pair_address_label.grid(
            row=0,
            column=2,
            padx=(60, 0),
            pady=pad_y,
            sticky="w"
        )

        self.wallet_proxy_label = customtkinter.CTkLabel(
            self.frame,
            text="Proxy",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_proxy_label.grid(
            row=0,
            column=3,
            padx=(80, 0),
            pady=pad_y,
            sticky="w"
        )

        self.wallet_status_label = customtkinter.CTkLabel(
            self.frame,
            text="Status",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.wallet_status_label.grid(
            row=0,
            column=4,
            padx=(95, 0),
            pady=pad_y,
            sticky="w"
        )

    def select_all_checkbox_event(self):
        checkbox_value = self.chose_all_checkbox.get()
        if checkbox_value:
            for wallet in self.wallet_items:
                wallet.chose_checkbox.select()

        else:
            for wallet in self.wallet_items:
                wallet.chose_checkbox.deselect()

        self.master.wallets_table.update_selected_wallets_labels()
