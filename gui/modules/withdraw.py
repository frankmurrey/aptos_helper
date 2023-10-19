import customtkinter


from src import enums
from src.schemas import tasks
from contracts.tokens.main import Tokens
from gui.modules.txn_settings_frame import TxnSettingFrame


class WithdrawLendingTab:
    def __init__(
            self,
            tabview,
            tab_name
    ):
        self.tabview = tabview

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        withdraw_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.withdraw_frame = WithdrawLendingFrame(
            master=self.tabview.tab(tab_name),
            grid=withdraw_frame_grid
        )

        self.txn_settings_frame = TxnSettingFrame(
            master=self.tabview.tab(tab_name),
            grid={
                "row": 1,
                "column": 0,
                "padx": 20,
                "pady": 20,
                "sticky": "nsew"
            }
        )

    def build_config_data(self):
        return tasks.AbelWithdrawTask(
            coin_x=self.withdraw_frame.token_to_withdraw_combobox.get(),
            gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
            gas_price=self.txn_settings_frame.gas_price_entry.get(),
            forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
        )


class WithdrawLendingFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid
    ):
        super().__init__(master)

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.protocol_label = customtkinter.CTkLabel(
            master=self,
            text="Protocol"
        )
        self.protocol_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.protocol_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_options,
            width=120,
            command=self.protocol_change_event
        )
        self.protocol_combobox.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        self.token_to_withdraw = customtkinter.CTkLabel(
            master=self,
            text="Token to Supply"
        )
        self.token_to_withdraw.grid(
            row=2,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        self.token_to_withdraw_combobox = customtkinter.CTkComboBox(
            master=self,
            values=self.protocol_coin_options,
            width=120
        )
        self.token_to_withdraw_combobox.grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 20)
        )

    @property
    def protocol_options(self) -> list:
        return [
            enums.ModuleName.ABEL.upper()
        ]

    @property
    def protocol_coin_options(self) -> list:
        tokens = Tokens()
        protocol = self.protocol_combobox.get()
        return [token.symbol.upper() for token in tokens.get_tokens_by_protocol(protocol)]

    def protocol_change_event(self, protocol=None):
        if protocol == enums.ModuleName.THE_APTOS_BRIDGE.upper():
            self.token_to_withdraw_combobox.configure(state="disabled")
            self.token_to_withdraw_combobox.configure(fg_color="#3f3f3f")

        else:
            self.token_to_withdraw_combobox.configure(state="normal")
            self.token_to_withdraw_combobox.configure(fg_color="#343638")
            coin_to_supply_options = self.protocol_coin_options
            self.token_to_withdraw_combobox.configure(values=coin_to_supply_options)
            self.token_to_withdraw_combobox.set(coin_to_supply_options[1])