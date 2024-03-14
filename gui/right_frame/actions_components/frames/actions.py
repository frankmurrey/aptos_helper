import tkinter.messagebox
from tkinter import Variable, filedialog
from typing import List, Dict, Union, Callable, TYPE_CHECKING
from uuid import UUID

import customtkinter
from loguru import logger

from gui.right_frame.actions_components.frames import ActionItemFrame
from gui.right_frame.wallets_table_frame import WalletsTable
from gui.right_frame.actions_components.frames import TableTopFrame
from gui.right_frame.actions_components.frames import CurrentActionsFrame
from gui.right_frame.actions_components.frames import ButtonActionsFrame
from gui.right_frame.actions_components.frames import RunSettingsFrame

from src.schemas.tasks import TaskBase
from src.schemas.wallet_data import WalletData
from src.tasks_executor import task_executor as task_executor
from src.storage import ActionStorage
from src.storage import Storage
from src import enums

from src.repr.repr_manager import repr_manager
from utils.file_manager import FileManager


if TYPE_CHECKING:
    from gui.right_frame.main_frame import RightFrame


class ActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.master: 'RightFrame' = master
        self.wallets_table: WalletsTable = self.master.wallets_table

        self.grid_rowconfigure((0, 1, 3, 4), weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.active_wallet = None

        self.failed_wallets_amount = 0
        self.completed_wallets_amount = 0

        self.wallets_completed_tasks: Dict[UUID, List[TaskBase]] = {}

        self.action_storage = ActionStorage()
        self.actions: List[dict] = []
        self.action_items: List[ActionItemFrame] = []

        self.current_wallet_action_items: List[ActionItemFrame] = []

        self.table_top_frame = TableTopFrame(master=self)
        self.current_actions_frame = CurrentActionsFrame(master=self)
        self.button_actions_frame = ButtonActionsFrame(master=self)

        self.actions_label = customtkinter.CTkLabel(
            self,
            text="Actions:",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.actions_label.grid(
            row=0,
            column=1,
            padx=0,
            pady=(10, 0),
            sticky="ws"
        )

        self.run_settings_label = customtkinter.CTkLabel(
            self,
            text="Run settings:",
            font=customtkinter.CTkFont(size=18, weight="bold")
        )
        self.run_settings_label.grid(
            row=0,
            column=2,
            padx=20,
            pady=(10, 0),
            sticky="ws"
        )
        self.run_settings_frame = RunSettingsFrame(master=self)

        self.start_button = customtkinter.CTkButton(
            self,
            text="Start",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30,
            command=self.on_start_button_click
        )
        self.start_button.grid(
            row=3,
            column=0,
            padx=20,
            pady=5,
            sticky="w"
        )

        self.stop_button = customtkinter.CTkButton(
            self,
            text="Stop",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30,
            fg_color="#db524b",
            hover_color="#5e1914",
            command=self.on_stop_button_click
        )
        self.stop_button.grid(
            row=3,
            column=0,
            padx=(150, 0),
            pady=5,
            sticky="w"
        )

    def set_task_exec_event_manager_callbacks(self):
        task_executor.event_manager.on_task_started(self.on_task_started)
        task_executor.event_manager.on_task_completed(self.on_task_completed)
        task_executor.event_manager.on_wallet_started(self.on_wallet_started)
        task_executor.event_manager.on_wallet_completed(self.on_wallet_completed)

    def get_wallet_actions(
            self,
            wallet_id: UUID
    ) -> List[TaskBase]:
        for key, values in self.wallets_completed_tasks.items():
            value: List[TaskBase]
            if key == wallet_id:
                return [task for task in values]

        return []

    @property
    def is_running(self):
        return task_executor.is_running()

    @property
    def tasks(self):
        tasks = []
        for action in self.actions:
            repeats = action["repeats"]
            task: TaskBase = action["task_config"]

            task.test_mode = bool(self.run_settings_frame.test_mode_checkbox.get())
            task.min_delay_sec = int(self.run_settings_frame.min_delay_entry_spinbox.entry.get())
            task.max_delay_sec = self.run_settings_frame.max_delay_entry_spinbox.entry.get()
            task.wait_for_receipt = bool(self.run_settings_frame.wait_for_receipt_checkbox.get())
            task.retries = int(self.run_settings_frame.retries_spinbox.entry.get())

            txn_wait_timeout_sec = self.run_settings_frame.txn_wait_timeout_seconds_spinbox.entry.get()
            task.txn_wait_timeout_sec = int(txn_wait_timeout_sec) if txn_wait_timeout_sec else 120

            task = TaskBase(**task.dict())

            for _ in range(repeats):
                tasks.append(task)

        return tasks

    def get_action_item_by_id(self, action_id: UUID) -> Union[ActionItemFrame, None]:
        if not self.action_items:
            return None

        for action_item in self.action_items:
            action_item: ActionItemFrame

            if action_item.task.task_id == action_id:
                return action_item

        return None

    def set_actions(
            self,
            actions: List[dict]
    ):
        try:
            self.actions = [*self.actions, *actions]
            self.redraw_current_actions_frame()

        except Exception as e:
            self.actions = []
            self.redraw_current_actions_frame()
            tkinter.messagebox.showerror(
                title="Error",
                message="Wrong actions config file"
            )

    def edit_action(
            self,
            action: dict
    ):
        if action is None:
            return

        try:
            for action_index, action_data in enumerate(self.actions):
                if action_data["task_config"].task_id == action["task_config"].task_id:
                    self.actions[action_index] = action

            self.redraw_current_actions_frame()

        except Exception as e:
            tkinter.messagebox.showerror(
                title="Error",
                message=str(e)
            )

    def set_action(
            self,
            action: dict
    ):
        if action is None:
            return

        try:
            self.actions.append(action)
            self.redraw_current_actions_frame()

        except Exception as e:
            tkinter.messagebox.showerror(
                title="Error",
                message=str(e)
            )

    def redraw_current_actions_frame(self):
        for action_item in self.action_items:
            action_item.grid_forget()
            action_item.destroy()

        self.action_items.clear()
        if not self.actions:
            self.current_actions_frame.no_actions_label.grid(
                row=0,
                column=0,
                padx=40,
                pady=10
            )
        else:
            try:
                self.current_actions_frame.no_actions_label.grid_forget()
            except AttributeError:
                pass

        start_row = 0
        start_column = 0

        for action_index, action_data in enumerate(self.actions):
            actions_item_grid = {
                "row": start_row + action_index,
                "column": start_column,
                "padx": 2,
                "pady": 4,
                "sticky": "ew"
            }

            action_item = ActionItemFrame(
                master=self.current_actions_frame,
                grid=actions_item_grid,
                repeats=action_data["repeats"],
                fg_color="grey21",
                task=action_data["task_config"],
                tab_name=action_data["tab_name"],
            )
            self.action_items.append(action_item)

    def remove_all_actions(self):
        if not self.actions:
            return

        msg_box = tkinter.messagebox.askyesno(
            title="Remove all",
            message="Are you sure you want to clear all actions?",
            icon="warning"
        )

        if not msg_box:
            return

        for action_item in self.action_items:
            action_item.grid_forget()
            action_item.destroy()

        self.actions = []
        self.action_items = []
        self.current_wallet_action_items = []
        self.redraw_current_actions_frame()

    def on_wallet_started(self, started_wallet: "WalletData"):

        wallet_item = self.wallets_table.get_wallet_item_by_wallet_id(wallet_id=started_wallet.wallet_id)
        self.active_wallet = wallet_item
        self.master.update_active_wallet_label(wallet_name=started_wallet.name)
        self.wallets_completed_tasks[started_wallet.wallet_id] = []
        wallet_item.set_wallet_active()

    def on_task_started(self, started_task: "TaskBase", current_wallet: "WalletData"):
        task_item = self.get_action_item_by_id(action_id=started_task.task_id)
        task_item.set_task_active()
        self.current_wallet_action_items.append(task_item)

    def on_task_completed(self, completed_task: "TaskBase", current_wallet: "WalletData"):
        action_item = self.get_action_item_by_id(action_id=completed_task.task_id)
        if action_item is None:
            return

        self.wallets_completed_tasks[current_wallet.wallet_id].append(completed_task)

        if completed_task.task_status == enums.TaskStatus.SUCCESS:
            action_item.set_task_completed()

        elif completed_task.task_status == enums.TaskStatus.FAILED:
            action_item.set_task_failed()

    def on_wallet_completed(self, completed_wallet: "WalletData"):
        wallet_item = self.wallets_table.get_wallet_item_by_wallet_id(wallet_id=completed_wallet.wallet_id)
        if not self.current_wallet_action_items:
            return

        self.completed_wallets_amount += 1
        if self.is_wallet_failed(wallet_id=completed_wallet.wallet_id):
            wallet_item.set_wallet_failed()
            self.failed_wallets_amount += 1
        else:
            wallet_item.set_wallet_completed()

        for action_item in self.current_wallet_action_items:
            action_item.set_task_empty()

        self.active_wallet = None
        self.master.update_wallets_stats_labels(
            completed_wallets=self.completed_wallets_amount,
            failed_wallets=self.failed_wallets_amount
        )

        self.master.update_active_wallet_label(wallet_name="None")

    def is_wallet_failed(self, wallet_id: UUID) -> bool:
        for key, values in self.wallets_completed_tasks.items():
            value: List[TaskBase]
            if key == wallet_id:
                for task in values:

                    if task.task_status == enums.TaskStatus.FAILED:
                        return True

        return False

    def on_start_button_click(self):

        if task_executor.is_running():
            return

        self.completed_wallets_amount = 0
        self.failed_wallets_amount = 0

        self.master.update_wallets_stats_labels(0, 0)

        for wallet_item in self.wallets_table.wallets_items:
            wallet_item.set_wallet_inactive()

        for action_item in self.action_items:
            action_item.set_task_empty()

        wallets = self.master.wallets_table.selected_wallets

        if not wallets:
            tkinter.messagebox.showerror(
                title="Error",
                message="No wallets selected"
            )
            return

        if not self.action_items:
            tkinter.messagebox.showerror(
                title="Error",
                message="No actions added"
            )
            return

        is_start = tkinter.messagebox.askyesno(
            title="Start",
            message="Are you sure you want to start?",
            icon="warning"
        )
        if not is_start:
            return

        if bool(self.run_settings_frame.test_mode_checkbox.get()):
            amount = Storage().app_config.wallets_amount_to_execute_in_test_mode
            wallets = wallets[:amount]

        task_executor.event_manager.clear_callbacks()
        self.set_task_exec_event_manager_callbacks()

        task_exec_run_mode = Storage().app_config.run_mode

        if task_exec_run_mode == enums.RunMode.SYNC:
            repr_manager.set_task_exec_callbacks(
                task_exec_event_manager=task_executor.event_manager
            )

        task_executor.process(
            wallets=wallets,
            tasks=self.tasks,
            shuffle_wallets=bool(self.run_settings_frame.shuffle_wallets_checkbox.get()),
            shuffle_tasks=bool(self.run_settings_frame.shuffle_task_checkbox.get()),

            run_mode=Storage().app_config.run_mode,
        )

    def on_stop_button_click(self):
        for action_item in self.action_items:
            action_item.set_task_empty()

        logger.critical("Stopped tasks processing")
        task_executor.stop()
