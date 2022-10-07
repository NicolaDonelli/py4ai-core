import os
from pathlib import Path
from typing import List, Union


def complete_path_split(path: str) -> List[str]:
    p, end = os.path.split(path)
    return complete_path_split(p) + [end] if p != "" else [end]


def create_dir_if_not_exists(directory: Union[str, Path]) -> Union[str, Path]:
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
