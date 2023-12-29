from typing import Callable, Union

import customtkinter
from pydantic.error_wrappers import ValidationError
from tkinter import Variable, messagebox
from loguru import logger

from src import enums
from src.schemas import tasks

from gui.objects import CTkCustomTextBox
from gui.modules.txn_settings_frame import TxnSettingFrame


class MerkleTab:
    def __init__(
            self,
            tabview,
            tab_name,
            task: Union[tasks.MerklePlaceOpenOrderTask, tasks.MerklePlaceCancelOrderTask]
    ):
        self.tabview = tabview
        self.tab_name = tab_name

        self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)

        supply_frame_grid = {
            "row": 0,
            "column": 0,
            "padx": 20,
            "pady": 20,
            "sticky": "nsew"
        }

        self.merkle_frame = MerkleFrame(
            master=self.tabview.tab(tab_name),
            grid=supply_frame_grid,
            task=task
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

    def get_config_schema(self) -> Union[Callable, None]:
        action = self.merkle_frame.action_combo.get().lower()
        if action == enums.ModuleType.PLACE_CANCEL_ORDER.value.lower():
            return tasks.MerklePlaceCancelOrderTask

        return tasks.MerklePlaceOpenOrderTask

    def build_config_data(self):
        config_schema = self.get_config_schema()
        if config_schema is None:
            logger.error("No config schema found")
            return None

        try:
            order_type = self.merkle_frame.order_type_combo.get().lower()
            action = self.merkle_frame.action_combo.get().lower()

            if action == enums.ModuleType.PLACE_CANCEL_ORDER.value.lower():
                order_type = enums.OrderType.LONG.value.lower()

            config_data = config_schema(
                min_amount_out=self.merkle_frame.min_amount_entry.get(),
                max_amount_out=self.merkle_frame.max_amount_entry.get(),
                use_all_balance=self.merkle_frame.use_all_balance_checkbox.get(),
                send_percent_balance=self.merkle_frame.send_percent_balance_checkbox.get(),
                gas_limit=self.txn_settings_frame.gas_limit_entry.get(),
                gas_price=self.txn_settings_frame.gas_price_entry.get(),
                forced_gas_limit=self.txn_settings_frame.forced_gas_limit_check_box.get(),
                reverse_action=self.merkle_frame.reverse_action_checkbox.get(),
                slippage=self.merkle_frame.slippage_entry.get(),
                pseudo_order=self.merkle_frame.pseudo_order_checkbox.get(),
                order_type=order_type,
            )

            return config_data

        except ValidationError as e:
            error_messages = "\n\n".join([error["msg"] for error in e.errors()])
            messagebox.showerror(
                title="Config validation error", message=error_messages
            )
            return None


class MerkleFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            grid,
            task: Union[tasks.MerklePlaceOpenOrderTask, tasks.MerklePlaceCancelOrderTask],
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.task = task

        self.grid(**grid)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

        # ORDER TYPE
        self.action_label = customtkinter.CTkLabel(
            master=self,
            text="Action:"
        )
        self.action_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        action = getattr(self.task, "module_type", enums.ModuleType.PLACE_OPEN_ORDER)
        self.action_combo = customtkinter.CTkComboBox(
            master=self,
            values=[
                enums.ModuleType.PLACE_OPEN_ORDER.value.title(),
                enums.ModuleType.PLACE_CANCEL_ORDER.value.title(),
            ],
            width=120,
            command=self.action_changed
        )
        self.action_combo.set(action.value.title())
        self.action_combo.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # ORDER TYPE
        self.order_type_label = customtkinter.CTkLabel(
            master=self,
            text="Order type:"
        )
        self.order_type_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=20,
            pady=(10, 0)
        )

        state = "disabled" if action == enums.ModuleType.PLACE_CANCEL_ORDER else "normal"
        order_type = getattr(self.task, "order_type", enums.OrderType.LONG)
        self.order_type_combo = customtkinter.CTkComboBox(
            master=self,
            values=[
                enums.OrderType.LONG.value.title(),
                enums.OrderType.SHORT.value.title(),
            ],
            width=120,
            state=state
        )
        self.order_type_combo.set(order_type.value.title())
        self.order_type_combo.grid(
            row=1,
            column=1,
            sticky="w",
            padx=20,
            pady=(0, 0)
        )

        # REVERSE ACTION CHECKBOX
        self.reverse_action_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Close position after opening",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            state=state
        )
        if getattr(self.task, "reverse_action", False):
            self.reverse_action_checkbox.select()

        self.reverse_action_checkbox.grid(
            row=3, column=0, padx=20, pady=(5, 0), sticky="w"
        )

        # MIN AMOUNT
        color = "#343638" if action == enums.ModuleType.PLACE_OPEN_ORDER else "#3f3f3f"
        self.min_amount_label = customtkinter.CTkLabel(self, text="Min amount:")
        self.min_amount_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")

        min_amount = getattr(self.task, "min_amount_out", "")
        self.min_amount_entry = customtkinter.CTkEntry(
            self,
            width=120,
            textvariable=Variable(value=min_amount),
            state=state,
            fg_color=color
        )
        self.min_amount_entry.grid(row=5, column=0, padx=20, pady=0, sticky="w")

        # MAX AMOUNT
        self.max_amount_label = customtkinter.CTkLabel(self, text="Max amount:")
        self.max_amount_label.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="w")

        max_amount = getattr(self.task, "max_amount_out", "")
        self.max_amount_entry = customtkinter.CTkEntry(
            self,
            width=120,
            textvariable=Variable(value=max_amount),
            state=state,
            fg_color=color
        )
        self.max_amount_entry.grid(row=5, column=1, padx=20, pady=0, sticky="w")

        # USE ALL BALANCE CHECKBOX
        self.use_all_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Use all balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            command=self.use_all_balance_checkbox_event,
            state=state
        )
        self.use_all_balance_checkbox.grid(
            row=6, column=0, padx=20, pady=(10, 0), sticky="w"
        )

        # SEND PERCENT BALANCE CHECKBOX
        self.send_percent_balance_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Send % of balance",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            state=state
        )
        self.send_percent_balance_checkbox.grid(
            row=7, column=0, padx=20, pady=(5, 0), sticky="w"
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

        # SLIPPAGE
        self.slippage_label = customtkinter.CTkLabel(self, text="Slippage (%):")
        self.slippage_label.grid(row=6, column=1, padx=20, pady=(10, 0), sticky="w")

        slippage = getattr(self.task, "slippage", 0.5)
        self.slippage_entry = customtkinter.CTkEntry(
            self, width=70, textvariable=Variable(value=slippage)
        )
        self.slippage_entry.grid(row=7, column=1, padx=20, pady=0, sticky="w")

        # PSEUDO ORDER
        self.pseudo_order_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Make pseudo order",
            onvalue=True,
            offvalue=False,
            checkbox_width=18,
            checkbox_height=18,
            state=state
        )
        if getattr(self.task, "pseudo_order", False):
            self.pseudo_order_checkbox.select()

        self.pseudo_order_checkbox.grid(
            row=8, column=0, padx=20, pady=(20, 0), sticky="w"
        )

        text = (f"Pair: APT/USDC\n"
                f"Pseudo order will not be actually executed, but will be "
                f"counted as executed for quest.")

        self.info_textbox = CTkCustomTextBox(
            master=self,
            grid={
                "row": 9,
                "column": 0,
                "padx": 20,
                "pady": (10, 20),
                "sticky": "nsew",
                "columnspan": 2
            },
            text=text,
        )

    def action_changed(self, *args):
        action = self.action_combo.get().lower()
        if action == enums.ModuleType.PLACE_CANCEL_ORDER:
            state = "disabled"
            self.order_type_combo.configure(state=state)

            self.reverse_action_checkbox.deselect()
            self.reverse_action_checkbox.configure(state=state)

            self.min_amount_entry.configure(state=state, fg_color="#3f3f3f", textvariable=Variable(value=""))
            self.max_amount_entry.configure(state=state, fg_color="#3f3f3f", textvariable=Variable(value=""))

            self.use_all_balance_checkbox.deselect()
            self.use_all_balance_checkbox.configure(state=state)

            self.send_percent_balance_checkbox.deselect()
            self.send_percent_balance_checkbox.configure(state=state)

            self.pseudo_order_checkbox.deselect()
            self.pseudo_order_checkbox.configure(state=state)

        else:
            state = "normal"
            self.order_type_combo.configure(state=state)

            self.reverse_action_checkbox.configure(state=state)

            self.min_amount_entry.configure(state=state, fg_color="#343638", textvariable=Variable(value=""))
            self.max_amount_entry.configure(state=state, fg_color="#343638", textvariable=Variable(value=""))

            self.use_all_balance_checkbox.configure(state=state)

            self.send_percent_balance_checkbox.configure(state=state)

            self.pseudo_order_checkbox.configure(state=state)

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
