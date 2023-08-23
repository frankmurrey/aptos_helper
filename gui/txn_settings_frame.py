import customtkinter

from tkinter import StringVar


class TxnSettingsFrameBlueprint(customtkinter.CTkFrame):
    def __init__(self, master,
                 is_common_fields_mark_need=False):
        super().__init__(master)

        self.is_common_fields_mark_need = is_common_fields_mark_need
        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(row=3, column=0, padx=15, pady=(15, 0), sticky="nsew")

        self.gas_price_entry = customtkinter.CTkEntry(self.frame,
                                                      width=70,
                                                      textvariable=StringVar(value="100"))

        self.gas_limit_entry = customtkinter.CTkEntry(self.frame,
                                                      width=70)

        self.force_gas_limit_checkbox = customtkinter.CTkCheckBox(self.frame,
                                                                  text="Force gas limit",
                                                                  checkbox_width=18,
                                                                  checkbox_height=18,
                                                                  onvalue=True,
                                                                  offvalue=False)

        self.min_delay_entry = customtkinter.CTkEntry(self.frame,
                                                      width=140,
                                                      textvariable=StringVar(value="20"))

        self.max_delay_entry = customtkinter.CTkEntry(self.frame,
                                                      width=140,
                                                      textvariable=StringVar(value="40"))

        self.wait_for_transaction_checkbox = customtkinter.CTkCheckBox(self.frame,
                                                                       text="Wait for transaction",
                                                                       checkbox_width=18,
                                                                       checkbox_height=18,
                                                                       onvalue=True,
                                                                       offvalue=False,
                                                                       command=self.wait_for_transaction_checkbox_event)

        self.transaction_wait_time_entry = customtkinter.CTkEntry(self.frame,
                                                                  width=140,
                                                                  state="disabled",
                                                                  fg_color='#3f3f3f')

        self.add_all_fields()

    def _add_gas_price_fields(self):
        if self.is_common_fields_mark_need:
            common_fields_mark_label = customtkinter.CTkLabel(self.frame,
                                                              text="*",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color='yellow')
            common_fields_mark_label.grid(row=0, column=0, padx=(85, 0), pady=(10, 0), sticky="w")

        gas_price_label = customtkinter.CTkLabel(self.frame,
                                                 text="Gas price:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        gas_price_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="w")
        self.gas_price_entry.grid(row=1, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_gas_limit_fields(self):
        if self.is_common_fields_mark_need:
            common_fields_mark_label = customtkinter.CTkLabel(self.frame,
                                                              text="*",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color='yellow')
            common_fields_mark_label.grid(row=0, column=0, padx=(168, 0), pady=(10, 0), sticky="w")

        gas_limit_label = customtkinter.CTkLabel(self.frame,
                                                 text="Gas limit:",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        gas_limit_label.grid(row=0, column=0, padx=(105, 0), pady=(10, 0), sticky="w")
        self.gas_limit_entry.grid(row=1, column=0, padx=(105, 0), pady=(0, 0), sticky="w")

    def _add_force_gas_limit_fields(self):
        self.force_gas_limit_checkbox.grid(row=2, column=0, padx=(20, 0), pady=(5, 5), sticky="w")

    def _add_min_delay_fields(self):
        if self.is_common_fields_mark_need:
            common_fields_mark_label = customtkinter.CTkLabel(self.frame,
                                                              text="*",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color='yellow')
            common_fields_mark_label.grid(row=3, column=0, padx=(122, 0), pady=(0, 0), sticky="w")

        min_delay_label = customtkinter.CTkLabel(self.frame,
                                                 text="Min delay (sec):",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        min_delay_label.grid(row=3, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.min_delay_entry.grid(row=4, column=0, padx=(20, 0), pady=(0, 0), sticky="w")

    def _add_max_delay_fields(self):
        if self.is_common_fields_mark_need:
            common_fields_mark_label = customtkinter.CTkLabel(self.frame,
                                                              text="*",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color='yellow')
            common_fields_mark_label.grid(row=3, column=1, padx=(106, 0), pady=(0, 0), sticky="w")
        max_delay_label = customtkinter.CTkLabel(self.frame,
                                                 text="Max delay (sec):",
                                                 font=customtkinter.CTkFont(size=12, weight="bold"))

        max_delay_label.grid(row=3, column=1, padx=(0, 20), pady=(0, 0), sticky="w")
        self.max_delay_entry.grid(row=4, column=1, padx=(0, 20), pady=(0, 0), sticky="w")

    def _add_transaction_wait_time_entry(self):
        if self.is_common_fields_mark_need:
            common_fields_mark_label = customtkinter.CTkLabel(self.frame,
                                                              text="*",
                                                              font=customtkinter.CTkFont(size=12, weight="bold"),
                                                              text_color='yellow')
            common_fields_mark_label.grid(row=5, column=0, padx=(200, 0), pady=(0, 0), sticky="w")
        transaction_wait_time_label = customtkinter.CTkLabel(self.frame,
                                                             text="Transaction wait time (sec):",
                                                             font=customtkinter.CTkFont(size=12, weight="bold"))

        transaction_wait_time_label.grid(row=5, column=0, padx=(20, 0), pady=(0, 0), sticky="w")
        self.transaction_wait_time_entry.grid(row=6, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def _add_wait_for_transaction_checkbox(self):
        self.wait_for_transaction_checkbox.grid(row=7, column=0, padx=(20, 0), pady=(0, 10), sticky="w")

    def wait_for_transaction_checkbox_event(self):
        checkbox_status = self.wait_for_transaction_checkbox.get()
        if checkbox_status is True:
            self.transaction_wait_time_entry.configure(state="normal", placeholder_text="120", fg_color='#343638')
        else:
            self.transaction_wait_time_entry.configure(placeholder_text="",
                                                       textvariable=StringVar(value=""),
                                                       fg_color='#3f3f3f')
            self.transaction_wait_time_entry.configure(state="disabled")

    def get_values(self):
        values = {
            "gas_price": self.gas_price_entry.get(),
            "gas_limit": self.gas_limit_entry.get(),
            "min_delay_sec": self.min_delay_entry.get(),
            "max_delay_sec": self.max_delay_entry.get(),
            "wait_for_receipt": self.wait_for_transaction_checkbox.get(),
            "txn_wait_timeout_sec": self.transaction_wait_time_entry.get()
        }

        return values

    def add_all_fields(self):
        self._add_gas_price_fields()
        self._add_gas_limit_fields()
        self._add_force_gas_limit_fields()
        self._add_min_delay_fields()
        self._add_max_delay_fields()
        self._add_transaction_wait_time_entry()
        self._add_wait_for_transaction_checkbox()




