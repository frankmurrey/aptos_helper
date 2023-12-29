import tkinter.messagebox
import tkinter.filedialog
from typing import Callable, Union, TYPE_CHECKING

import customtkinter

from utils.file_manager import FileManager
from gui.interactions_window.top_level import InteractionsTopLevelWindow

if TYPE_CHECKING:
    from gui.right_frame.actions_components import ActionsFrame


class ButtonActionsFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master: any,
            **kwargs
    ):
        super().__init__(master=master, **kwargs)
        self.master: 'ActionsFrame' = master
        self.actions_top_level_window = None
        self.actions_edit_top_level_window = None

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
            command=self.master.remove_all_actions
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

    def add_action_callback(self, action: dict):
        self.master.set_actions([action])

    def add_action_button_event(self):
        geometry = "500x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "500x900+1000+100"

        if self.actions_top_level_window is None or not self.actions_top_level_window.winfo_exists():
            self.actions_top_level_window = InteractionsTopLevelWindow(
                master=self.master,
                on_action_save=self.add_action_callback,
            )
            self.actions_top_level_window.geometry(geometry)
            self.actions_top_level_window.resizable(False, False)
        else:
            self.actions_top_level_window.focus()

    def close_edit_action_window(self):
        if self.actions_edit_top_level_window is not None and self.actions_edit_top_level_window.winfo_exists():
            self.actions_edit_top_level_window.destroy()
            self.actions_edit_top_level_window = None

    def edit_action_button_event(
            self,
            on_action_save: Callable[[Union[dict, None]], None],
            action: dict
    ):
        geometry = "500x900+1505+100"
        if self.winfo_screenwidth() <= 1600:
            geometry = "500x900+1000+100"

        if self.actions_edit_top_level_window is None or not self.actions_edit_top_level_window.winfo_exists():
            self.actions_edit_top_level_window = InteractionsTopLevelWindow(
                master=self.master,
                action=action,
                on_action_save=on_action_save,
                title="Edit action"
            )
            self.actions_edit_top_level_window.geometry(geometry)
            self.actions_edit_top_level_window.resizable(False, False)
            self.actions_edit_top_level_window.protocol("WM_DELETE_WINDOW", self.close_edit_action_window)
        else:
            self.actions_edit_top_level_window.focus()

    def save_actions_cfg_button_event(self):
        actions = self.master.actions
        run_settings_frame = self.master.run_settings_frame
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

        self.master.remove_all_actions()
        self.master.set_actions(actions)
        self.master.run_settings_frame.upload_from_config(run_settings_config)