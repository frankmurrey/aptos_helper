import tkinter.messagebox
from tkinter import Variable
from typing import Callable, Union, TYPE_CHECKING

import customtkinter

from gui import modules
from gui.interactions_window.module_select_frame import ModuleSelectFrame

from src import enums
from src.schemas import tasks


if TYPE_CHECKING:
    from gui.right_frame.actions_components.frames.actions import ActionsFrame


class Tab:
    def __init__(
            self,
            tab,
            spinbox_max_value: Union[int, float] = 100,
            spinbox_start_value: Union[int, float] = 1,
    ):
        self.tab = tab
        self.spinbox_max_value = spinbox_max_value
        self.spinbox_start_value = spinbox_start_value


TABS: dict = {
    enums.TabName.SWAP: Tab(
        tab=modules.SwapTab,
    ),
    enums.TabName.ADD_LIQUIDITY: Tab(
        tab=modules.AddLiquidityTab,
    ),
    enums.TabName.REMOVE_LIQUIDITY: Tab(
        tab=modules.RemoveLiquidityTab,
        spinbox_max_value=1,
    ),
    enums.TabName.SUPPLY_LENDING: Tab(
        tab=modules.SupplyLendingTab,
    ),
    enums.TabName.DEPOSIT: Tab(
        tab=modules.DepositLendingTab,
    ),
    enums.TabName.WITHDRAW: Tab(
        tab=modules.WithdrawLendingTab,
        spinbox_max_value=1,
    ),
    enums.TabName.DELEGATE: Tab(
        tab=modules.DelegateTab,
        spinbox_max_value=1,
    ),
    enums.TabName.UNLOCK: Tab(
        tab=modules.UnlockTab,
        spinbox_max_value=1,
    ),
    enums.TabName.TRANSFER: Tab(
        tab=modules.TransferTab,
    ),
    enums.TabName.BRIDGE: Tab(
        tab=modules.TheAptosBridgeTab,
    ),
    enums.TabName.NFT_COLLECT: Tab(
        tab=modules.NftCollectTab,
        spinbox_max_value=1,
    ),
    enums.TabName.MERKLE: Tab(
        tab=modules.MerkleTab,
    ),
    enums.TabName.MINT: Tab(
        tab=modules.MintTab,
    ),
    enums.TabName.UNSTAKE: Tab(
        tab=modules.UnstakeTab,
    ),
}


class InteractionsTopLevelWindow(customtkinter.CTkToplevel):
    def __init__(
            self,
            master,
            action: dict = None,
            on_action_save: Callable[[Union[dict, None]], None] = None,
            title: str = "New action"
    ):
        super().__init__()

        self.master: 'ActionsFrame' = master
        self.action = action
        self.task = action["task_config"] if action else None
        self.on_action_save = on_action_save

        self.title(title)

        self.after(10, self.focus_force)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)

        self.current_tab_name = None
        self.current_tab = None

        self.chose_module_frame = ModuleSelectFrame(
            master=self,
            action=action
        )

        self.tabview = customtkinter.CTkTabview(
            self,
            width=300,
            height=600
        )
        self.tabview.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="nsew"
        )
        self.tabview.grid_columnconfigure(0, weight=1)
        self.tabview.grid_rowconfigure(0, weight=1)

        if self.action:
            self.set_edit_tab()
        else:
            self.set_default_tab()

        self.confirm_button = customtkinter.CTkButton(
            self,
            text="Save",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=100,
            height=35,
            command=self.confirm_button_event
        )
        self.confirm_button.grid(
            row=2,
            column=0,
            padx=40,
            pady=(0, 20),
            sticky="w"
        )

        self.after(10, self.focus_force)

    def set_new_tab(
            self,
            tab_name: str
    ):
        if self.current_tab_name is not None:
            self.tabview.delete(self.current_tab_name)

        self.tabview.add(tab_name)
        self.tabview.set(tab_name)

        tab: Tab = TABS[enums.TabName(tab_name)]
        self.current_tab = tab.tab(
            self.tabview,
            tab_name,
            self.task
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.max_value = tab.spinbox_max_value
        self.chose_module_frame.float_spinbox.entry.configure(textvariable=Variable(value=1))

    def set_default_tab(self):
        tab_name = self.chose_module_frame.modules_option_menu.get()
        self.tabview.add(tab_name.title())
        self.tabview.set(tab_name.title())
        self.current_tab = modules.SwapTab(
            self.tabview,
            tab_name
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.max_value = 100
        self.chose_module_frame.float_spinbox.entry.configure(textvariable=Variable(value=1))

    def set_edit_tab(self):
        tab_name = self.action["tab_name"]
        self.tabview.add(tab_name.title())
        self.tabview.set(tab_name.title())
        self.current_tab = TABS[enums.TabName(tab_name)].tab(
            self.tabview,
            tab_name.title(),
            self.task
        )
        self.current_tab_name = tab_name
        self.chose_module_frame.float_spinbox.entry.configure(
            textvariable=Variable(value=self.action["repeats"])
        )
        self.chose_module_frame.probability_spinbox.entry.configure(
            textvariable=Variable(value=self.action["task_config"].probability)
        )

    def get_repeats_amount(self) -> Union[int, None]:
        try:
            repeats = int(self.chose_module_frame.float_spinbox.get())
            if repeats < 1:
                return None
            return repeats

        except ValueError:
            return None

    def confirm_button_event(self):
        if self.master.is_running:
            tkinter.messagebox.showerror("Error", "You can't edit action while it's running")
            return

        current_tab = self.current_tab
        if current_tab is None:
            return

        config_data: tasks.TaskBase = current_tab.build_config_data()
        if config_data is None:
            self.focus_force()
            return

        probability = self.chose_module_frame.probability_spinbox.get()

        try:
            probability = int(probability)
        except ValueError:
            tkinter.messagebox.showerror(
                title="Error",
                message="Probability must be a positive integer"
            )
            return

        config_data.probability = int(probability)

        if self.action:
            config_data.task_id = self.action["task_config"].task_id

        repeats = self.get_repeats_amount()
        if repeats is None:
            tkinter.messagebox.showerror(
                title="Error",
                message="Repeats amount must be a positive integer"
            )
            return

        self.on_action_save(
            {
                "task_config": config_data,
                "repeats": repeats,
                "tab_name": self.current_tab_name
            }
        )
        if self.action:
            self.master.button_actions_frame.close_edit_action_window()
