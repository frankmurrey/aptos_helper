import os
import subprocess
import functools
from typing import Tuple, List

from src import paths


@functools.cache
def is_windows() -> bool:
    return os.name == "nt"


@functools.cache
def is_linux() -> bool:
    return os.name == "posix"


@functools.cache
def get_missed_requirements() -> List[str]:
    """
    Get requirements that are not installed.
    Returns: list of missing requirements
    """

    with open(os.path.join(paths.MAIN_DIR, "req.txt"), "r", encoding="utf-16") as f:
        requirements = f.readlines()
        requirements = [
            req.split("==")[0].strip().lower()
            for req in requirements
        ]

    exec_result = (
        subprocess.check_output(["pip", "freeze"])
        .decode("utf-8")
        .lower()
    )
    installed_requirements = [
        req.split("==")[0].strip().lower()
        for req in exec_result.splitlines()
    ]

    missed_requirements = []
    for req in requirements:
        if req not in installed_requirements:
            missed_requirements.append(req)

    return missed_requirements
