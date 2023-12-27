from tkinter import messagebox

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable


from gui.modules.txn_settings_frame import TxnSettingFrame
from contracts.chains.main import Chains
from src.schemas import tasks


class TheAptosBridgeTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: tasks.TheAptosBridgeTask = None,
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        bridge_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.bridge_frame = BridgeFrame(
            master=self.tabview.tab(tab_name),
            grid=bridge_frame_grid,
            task=task,
        )

        txn_settings_frame_grid = {
            "row": 1,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew",
        }

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid=txn_settings_frame_grid,
        )

    def build_config_data(self):
        try:
            config_schema = tasks.TheAptosBridgeTask(
                coin_x=self.bridge_frame.coin_x_combobox.get(),
                dst_chain_name=self.bridge_frame.dst_chain_combobox.get(),
                min_amount_out=self.bridge_frame.min_amount_entry.get(),
                max_amount_out=self.bridge_frame.max_amount_entry.get(),
                use_all_balance=self.bridge_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.bridge_frame.send_percent_balance_checkbox.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get()
            )

            return config_schema

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class BridgeFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: tasks.TheAptosBridgeTask,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1, uniform="a")
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # DST CHAIN
        self.dst_chain_name_label = customtkinter.CTkLabel(
            self,
            text="Dst chain:",
        )
        self.dst_chain_name_label.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        self.dst_chain_combobox = customtkinter.CTkComboBox(
            self,
            values=self.dst_chain_options,
            width=130,
            command=self.update_coin_options

        )
        dst_chain = getattr(self.task, "dst_chain_name", "BSC")
        self.dst_chain_combobox.set(dst_chain.upper())
        self.dst_chain_combobox.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # COIN X
        self.coin_x_label = customtkinter.CTkLabel(
            self,
            text="Coin to bridge:",
        )
        self.coin_x_label.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="w")

        self.coin_x_combobox = customtkinter.CTkComboBox(
            self,
            values=self.dst_coin_options,
            width=130,
        )
        coin_x = getattr(self.task, "coin_x", self.dst_coin_options[0])
        self.coin_x_combobox.set(coin_x.upper())
        self.coin_x_combobox.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="w")

        # MIN AMOUNT
        self.min_amount_label = customtkinter.CTkLabel(self, text="Min amount:")
        self.min_amount_label.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")

        min_amount = getattr(self.task, "min_amount_out", 1)
        self.min_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=min_amount))
        self.min_amount_entry.grid(row=3, column=0, padx=20, pady=0, sticky="w")

        # MAX AMOUNT
        self.max_amount_label = customtkinter.CTkLabel(self, text="Max amount:")
        self.max_amount_label.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")

        max_amount = getattr(self.task, "max_amount_out", 2)
        self.max_amount_entry = customtkinter.CTkEntry(self, width=120, textvariable=Variable(value=max_amount))
        self.max_amount_entry.grid(row=3, column=1, padx=20, pady=0, sticky="w")

        # USE ALL BALANCE
        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event,
        )
        self.use_all_balance_checkbox.grid(
            row=4, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
        )
        self.send_percent_balance_checkbox.grid(
            row=5, column=0, padx=20, pady=(5, 20), sticky="w"
        )
        if getattr(self.task, "send_percent_balance", False):
            self.send_percent_balance_checkbox.select()

        if getattr(self.task, "use_all_balance", False):
            self.use_all_balance_checkbox.select()
            self.min_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled",
                fg_color='#3f3f3f',
                textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(
                state="disabled"
            )

    @property
    def dst_chain_options(self):
        all_chains = Chains().all_chains
        return [chain.name for chain in all_chains]

    @property
    def dst_coin_options(self):
        current_chain = self.dst_chain_combobox.get()
        current_chain_obj = Chains().get_by_name(current_chain)
        return current_chain_obj.supported_tokens

    def update_coin_options(self, chain_value):
        current_chain_obj = Chains().get_by_name(chain_value)
        self.coin_x_combobox.configure(values=current_chain_obj.supported_tokens)
        self.coin_x_combobox.set(current_chain_obj.supported_tokens[0])

    def use_all_balance_checkbox_event(self):
        if self.use_all_balance_checkbox.get():
            self.min_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="disabled", fg_color="#3f3f3f", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(state="disabled")
        else:
            self.min_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.max_amount_entry.configure(
                state="normal", fg_color="#343638", textvariable=Variable(value="")
            )
            self.send_percent_balance_checkbox.configure(state="normal")
