import random
from typing import Optional, Type, Union, List
from typing import TYPE_CHECKING

import config

if TYPE_CHECKING:
    from src.schemas.tasks.base.base import TaskBase
    from src.schemas.action_models import ModuleExecutionResult


def get_time_to_sleep(
        task: "TaskBase",
        task_result: Optional["ModuleExecutionResult"],
) -> float:
    """
    Get time to sleep
    Args:
        task: processed task
        task_result: result of processed task
    Returns: time to sleep after task processing
    """
    if not task_result or task.test_mode:
        return config.DEFAULT_DELAY_SEC
    else:
        return random.uniform(
            task.min_delay_sec,
            task.max_delay_sec
        )


def is_task_virtual(
        task: Union["TaskBase", Type["TaskBase"]],
) -> bool:
    """
    Check if task is virtual
    Args:
        task: task (or task model) to check
    Returns: True if task is virtual, False otherwise

    """
    return getattr(task, config.VIRTUAL_TASK_PARAMETER, False)


def create_virtual_task(
        base_task: "TaskBase"
):
    """
    Create virtual task from base task
    Args:
        base_task: task to create virtual task from
    Returns: virtual task
    """

    for task_class in base_task.__class__.__subclasses__():
        if is_task_virtual(task_class):
            virtual_task = task_class(**base_task.dict(
                exclude={"reverse_action", "reverse_action_task"},
            ))

            return virtual_task
    else:
        raise ValueError(f"Task \"{base_task.__class__.__name__}\" not have virtual task!")


def fill_with_virtual_tasks(
        actual_tasks: List["TaskBase"],
) -> List["TaskBase"]:
    """
    Fill tasks with virtual tasks if needed
    Args:
        actual_tasks: actual tasks
    Returns: tasks with virtual tasks
    """

    tasks_to_fill = actual_tasks.copy()

    for task_index, task in enumerate(tasks_to_fill):
        if task.reverse_action:
            virtual_task = create_virtual_task(task)

            tasks_to_fill[task_index].min_delay_sec = task.reverse_action_min_delay_sec
            tasks_to_fill[task_index].max_delay_sec = task.reverse_action_max_delay_sec

            tasks_to_fill.insert(task_index + 1, virtual_task)

    return tasks_to_fill
