import tkinter.messagebox
from tkinter import Variable, filedialog
from typing import List, Union
from uuid import UUID

import customtkinter
from loguru import logger

from src.schemas.tasks.base.base import TaskBase
from src.schemas.wallet_data import WalletData
from src.tasks_executor import tasks_executor
from src.storage import ActionStorage
from src.storage import Storage
from src.file_manager import FileManager
from gui.main_window.interactions_top_level_window import InteractionTopLevelWindow
from gui.main_window.wallet_action_frame import WalletActionFrame
from gui.modules.frames import FloatSpinbox
from gui.wallet_right_window.wallets_table import WalletsTable
from src import enums


class ActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        tasks_executor.event_manager.on_wallet_started(self.on_wallet_started)
        tasks_executor.event_manager.on_task_started(self.on_task_started)

        tasks_executor.event_manager.on_task_completed(self.on_task_completed)
        tasks_executor.event_manager.on_wallet_completed(self.on_wallet_completed)

        self.master = master
        self.wallets_table: WalletsTable = self.master.wallets_table

        self.app_config = Storage().app_config

        self.grid_rowconfigure((0, 1, 3, 4), weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.action_storage = ActionStorage()
        self.actions: List[dict] = []
        self.action_items: List[WalletActionFrame] = []

        self.current_wallet_action_items: List[WalletActionFrame] = []

        self.table_top_frame = TableTopFrame(master=self)
        self.current_actions_frame = CurrentActionsFrame(master=self)
        self.button_actions_frame = ButtonActionsFrame(parent=self)

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
        self.run_settings_frame = RunSettingsFrame(parent=self)

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

            txn_wait_timeout_sec = self.run_settings_frame.txn_wait_timeout_seconds_spinbox.entry.get()
            task.txn_wait_timeout_sec = int(txn_wait_timeout_sec) if txn_wait_timeout_sec else 120

            task = TaskBase(**task.dict())

            for _ in range(repeats):
                tasks.append(task)

        return tasks

    def get_action_item_by_id(self, action_id: UUID) -> Union[WalletActionFrame, None]:
        if not self.action_items:
            return None

        for action_item in self.action_items:
            action_item: WalletActionFrame

            if action_item.task.task_id == action_id:
                return action_item

        return None

    def set_actions(
            self,
            actions: List[dict]
    ):
        try:
            self.actions = actions
            self.redraw_current_actions_frame()

        except Exception as e:
            self.actions = []
            self.redraw_current_actions_frame()
            tkinter.messagebox.showerror(
                title="Error",
                message="Wrong actions config file"
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

            action_item = WalletActionFrame(
                master=self.current_actions_frame,
                grid=actions_item_grid,
                repeats=action_data["repeats"],
                fg_color="grey21",
                task=action_data["task_config"],
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
        wallet_item.set_wallet_active()

    def on_task_started(self, started_task: "TaskBase", current_wallet: "WalletData"):
        task_item = self.get_action_item_by_id(action_id=started_task.task_id)
        task_item.set_task_active()
        self.current_wallet_action_items.append(task_item)

    def on_task_completed(self, completed_task: "TaskBase", current_wallet: "WalletData"):
        action_item = self.get_action_item_by_id(action_id=completed_task.task_id)
        if action_item is None:
            return

        if completed_task.task_status == enums.TaskStatus.SUCCESS:
            action_item.set_task_completed()
        else:
            action_item.set_task_failed()

    def on_wallet_completed(self, completed_wallet: "WalletData"):
        wallet_item = self.wallets_table.get_wallet_item_by_wallet_id(wallet_id=completed_wallet.wallet_id)
        wallet_item.set_wallet_completed()
        if not self.current_wallet_action_items:
            return

        for action_item in self.current_wallet_action_items:
            action_item.set_task_empty()

    def on_start_button_click(self):

        if tasks_executor.is_running():
            return

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

        yesno = tkinter.messagebox.askyesno(
            title="Start",
            message="Are you sure you want to start?",
            icon="warning"
        )
        if not yesno:
            return

        if bool(self.run_settings_frame.test_mode_checkbox.get()):
            amount = self.app_config.wallets_amount_to_execute_in_test_mode
            wallets = wallets[:amount]

        tasks_executor.process(
            wallets=wallets,
            tasks=self.tasks,
            shuffle_wallets=bool(self.run_settings_frame.shuffle_wallets_checkbox.get()),
            shuffle_tasks=bool(self.run_settings_frame.shuffle_task_checkbox.get()),
        )

    def on_stop_button_click(self):
        logger.critical("Tasks processing stopped")
        tasks_executor.stop()


class TableTopFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 0),
            sticky="nsew"
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="uniform")

        self.action_name_label = customtkinter.CTkLabel(
            self,
            text="Module",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_name_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=0
        )

        self.action_type_label = customtkinter.CTkLabel(
            self,
            text="Action",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )

        self.action_type_label.grid(
            row=0,
            column=1,
            padx=15,
            pady=0
        )

        self.repeats_label = customtkinter.CTkLabel(
            self,
            text="Info",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.repeats_label.grid(
            row=0,
            column=2,
            padx=15,
            pady=0
        )

        self.action_info_label = customtkinter.CTkLabel(
            self,
            text="Repeats",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.action_info_label.grid(
            row=0,
            column=3,
            padx=30,
            pady=0
        )


class CurrentActionsFrame(customtkinter.CTkScrollableFrame):
    def __init__(
            self,
            master: any,
            **kwargs):
        super().__init__(master, **kwargs)

        self.grid(
            row=1,
            column=0,
            padx=20,
            pady=(10, 20),
            sticky="nsew"
        )
        self.grid_columnconfigure(0, weight=1)

        self.no_actions_label = customtkinter.CTkLabel(
            self,
            text="No actions",
            font=customtkinter.CTkFont(size=15, weight="bold")
        )
        self.no_actions_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=10
        )


class ButtonActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            parent: any,
            **kwargs):
        super().__init__(master=parent, **kwargs)
        self.parent: ActionsFrame = parent
        self.actions_top_level_window = None

        self.grid_rowconfigure((0, 1, 2, 3), weight=0)
        self.grid_columnconfigure(0, weight=0)

        self.grid(
            row=1,
            column=1,
            padx=(0, 10),
            pady=(10, 20),
            sticky="nsew"
        )
        self.add_action_button = customtkinter.CTkButton(
            self,
            text="Add action",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30,
            command=self.add_action_button_event
        )
        self.add_action_button.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="ew"
        )

        self.remove_all_actions_button = customtkinter.CTkButton(
            self,
            text="Clear all",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            fg_color="#db524b",
            hover_color="#5e1914",
            width=110,
            height=30,
            command=self.parent.remove_all_actions
        )

        self.remove_all_actions_button.grid(
            row=1,
            column=0,
            padx=20,
            pady=(0, 50),
            sticky="ew"
        )

        self.save_actions_cfg_button = customtkinter.CTkButton(
            self,
            text="Save config",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30,
            fg_color="#5c24ec",
            hover_color='#430278',
            command=self.save_actions_cfg_button_event
        )

        self.save_actions_cfg_button.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        self.upload_actions_cfg_button = customtkinter.CTkButton(
            self,
            text="Load config",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            width=110,
            height=30,
            fg_color='#5c24ec',
            hover_color='#430278',
            command=self.upload_actions_cfg_button_event
        )

        self.upload_actions_cfg_button.grid(
            row=3,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

    def add_action_button_event(self):
        if self.actions_top_level_window is None or not self.actions_top_level_window.winfo_exists():
            self.actions_top_level_window = InteractionTopLevelWindow(parent=self.master)
            self.actions_top_level_window.geometry("500x950+1505+100")
            self.actions_top_level_window.resizable(False, False)
        else:
            self.actions_top_level_window.focus()

    def save_actions_cfg_button_event(self):
        actions = self.parent.actions
        run_settings_frame = self.parent.run_settings_frame
        cfg = run_settings_frame.build_config()

        data = {
            "actions": actions,
            "run_settings_config": cfg
        }

        if not actions:
            tkinter.messagebox.showerror(
                title="Error",
                message="No actions added"
            )
            return

        file_path = tkinter.filedialog.asksaveasfilename(
            initialfile="actions_config.pkl",
            title="Save actions config",
            filetypes=(("pickle files", "*.pkl"),)
        )
        FileManager.save_to_pickle_file(data, file_path)

    def upload_actions_cfg_button_event(self):
        file_path = tkinter.filedialog.askopenfilename(
            title="Select actions config file",
            filetypes=(("pickle files", "*.pkl"),)
        )
        if not file_path:
            return

        data = FileManager.read_from_pickle_file(file_path)

        if not data:
            tkinter.messagebox.showerror(
                title="Error",
                message="Can't read actions config file"
            )
            return

        actions = data.get("actions")
        run_settings_config = data.get("run_settings_config")
        if not actions or not run_settings_config:
            tkinter.messagebox.showerror(
                title="Error",
                message="Can't read actions config file"
            )
            return

        self.parent.set_actions(actions)
        self.parent.run_settings_frame.upload_from_config(run_settings_config)


class RunSettingsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            parent: any,
            **kwargs):
        super().__init__(master=parent, **kwargs)
        self.parent = parent

        self.grid(
            row=1,
            column=2,
            padx=20,
            pady=(10, 20),
            sticky="nsew",
            rowspan=2
        )

        self.grid_columnconfigure((0, 1), weight=1)

        self.test_mode_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Test mode",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.test_mode_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.test_mode_checkbox.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        self.shuffle_wallets_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Shuffle wallets",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.shuffle_wallets_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.shuffle_wallets_checkbox.grid(
            row=0,
            column=1,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        self.shuffle_task_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Shuffle tasks",
            text_color="#F47174",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.shuffle_task_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.shuffle_task_checkbox.grid(
            row=1,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky="ew"
        )

        self.min_delay_label = customtkinter.CTkLabel(
            self,
            text="Min delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.min_delay_label.grid(
            row=2,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.min_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.min_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=40)
        )
        self.min_delay_entry_spinbox.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        self.max_delay_label = customtkinter.CTkLabel(
            self,
            text="Max delay (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.max_delay_label.grid(
            row=2,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.max_delay_entry_spinbox = FloatSpinbox(self,
                                                    step_size=5,
                                                    width=105)
        self.max_delay_entry_spinbox.entry.configure(
            textvariable=Variable(value=80)
        )
        self.max_delay_entry_spinbox.grid(
            row=3,
            column=1,
            padx=20,
            pady=(0, 10),
            sticky="w"
        )

        txn_wait_timeout_seconds_label = customtkinter.CTkLabel(
            self,
            text="Wait timeout (sec):",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        txn_wait_timeout_seconds_label.grid(
            row=4,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.txn_wait_timeout_seconds_spinbox = FloatSpinbox(self,
                                                             step_size=5,
                                                             width=105)
        self.txn_wait_timeout_seconds_spinbox.entry.configure(
            state="normal",
            textvariable=Variable(value=120)
        )
        self.txn_wait_timeout_seconds_spinbox.add_button.configure(
            state="normal"
        )
        self.txn_wait_timeout_seconds_spinbox.grid(
            row=5,
            column=0,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.wait_for_receipt_checkbox = customtkinter.CTkCheckBox(
            self,
            text="Wait for txn",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self.wait_for_txn_checkbox_event,
            onvalue=True,
            offvalue=False
        )
        self.wait_for_receipt_checkbox.grid(
            row=6,
            column=0,
            padx=20,
            pady=(10, 10),
            sticky="w"
        )
        self.wait_for_receipt_checkbox.select()

        self.retries_label = customtkinter.CTkLabel(
            self,
            text="Retries:",
            font=customtkinter.CTkFont(size=12, weight="bold")
        )
        self.retries_label.grid(
            row=4,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

        self.retries_spinbox = FloatSpinbox(self,
                                            start_index=1,
                                            step_size=1,
                                            width=105)
        self.retries_spinbox.entry.configure(
            textvariable=Variable(value=3)
        )
        self.retries_spinbox.grid(
            row=5,
            column=1,
            padx=20,
            pady=0,
            sticky="w"
        )

    def build_config(self):
        run_settings_cfg = {
            "test_mode": self.test_mode_checkbox.get(),
            "min_delay_sec": self.min_delay_entry_spinbox.entry.get(),
            "max_delay_sec": self.max_delay_entry_spinbox.entry.get(),
            "wait_for_receipt": self.wait_for_receipt_checkbox.get(),
            "txn_wait_timeout_sec": self.txn_wait_timeout_seconds_spinbox.entry.get(),
            "shuffle_wallets": self.shuffle_wallets_checkbox.get(),
            "retries": self.retries_spinbox.entry.get()
        }

        return run_settings_cfg

    def upload_from_config(self, run_settings_cfg: dict):
        try:
            if not run_settings_cfg:
                return

            if run_settings_cfg["test_mode"]:
                self.test_mode_checkbox.select()
                self.test_mode_checkbox_event()
            else:
                self.test_mode_checkbox.deselect()
                self.test_mode_checkbox_event()

            if run_settings_cfg["shuffle_wallets"]:
                self.shuffle_wallets_checkbox.select()
                self.shuffle_wallets_checkbox_event()
            else:
                self.shuffle_wallets_checkbox.deselect()
                self.shuffle_wallets_checkbox_event()

            self.min_delay_entry_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["min_delay_sec"])
            )
            self.max_delay_entry_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["max_delay_sec"])
            )

            if run_settings_cfg['wait_for_receipt']:
                self.wait_for_receipt_checkbox.select()
                self.wait_for_txn_checkbox_event()
                self.txn_wait_timeout_seconds_spinbox.entry.configure(
                    textvariable=Variable(value=run_settings_cfg["txn_wait_timeout_sec"])
                )
            else:
                self.wait_for_receipt_checkbox.deselect()
                self.wait_for_txn_checkbox_event()

            self.retries_spinbox.entry.configure(
                textvariable=Variable(value=run_settings_cfg["retries"])
            )

        except Exception as e:
            tkinter.messagebox.showerror(
                title="Error",
                message=str(e)
            )

    def wait_for_txn_checkbox_event(self):
        if self.wait_for_receipt_checkbox.get():
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="normal",
                fg_color="gray16",
                textvariable=Variable(value=120)
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="normal")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="normal")
        else:
            self.txn_wait_timeout_seconds_spinbox.entry.configure(
                state="disabled",
                fg_color="#3f3f3f",
                textvariable=Variable(value="")
            )
            self.txn_wait_timeout_seconds_spinbox.add_button.configure(
                state="disabled")

            self.txn_wait_timeout_seconds_spinbox.subtract_button.configure(
                state="disabled")

    def test_mode_checkbox_event(self):
        if self.test_mode_checkbox.get():
            self.test_mode_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.test_mode_checkbox.configure(
                text_color="#F47174"
            )

    def shuffle_wallets_checkbox_event(self):
        if self.shuffle_wallets_checkbox.get():
            self.shuffle_wallets_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.shuffle_wallets_checkbox.configure(
                text_color="#F47174"
            )

    def shuffle_task_checkbox_event(self):
        if self.shuffle_task_checkbox.get():
            self.shuffle_task_checkbox.configure(
                text_color="#6fc276"
            )
        else:
            self.shuffle_task_checkbox.configure(
                text_color="#F47174"
            )