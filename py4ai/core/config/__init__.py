"""Implementation of classes that parse configuration files."""
import os
import re
from functools import reduce
from glob import glob
from typing import Optional, Sequence, Union

from cfg_load import Configuration, load
from yaml import (
    FullLoader,
    Loader,
    Node,
    SequenceNode,
    UnsafeLoader,
    add_constructor,
    add_implicit_resolver,
)

from py4ai.core.types import PathLike

env_var_matcher = re.compile(r"\$\{([^}^{]+)\}")


def path_constructor(
    loader: Union[Loader, FullLoader, UnsafeLoader], node: Node
) -> PathLike:
    """
    Extract the matched value, expand env variable, and replace the match.

    :param loader: not used
    :param node: YAML node
    :return: path
    :raises SyntaxError: if the node value does not match the regex expression for a path-like string
    :raises KeyError: raises an exception if the environment variable is missing
    """
    value = node.value
    match = env_var_matcher.match(value)

    if match is None:
        raise SyntaxError("Can't match pattern")

    env_var = match.group()[2:-1]
    try:
        return os.environ[env_var] + value[match.end() :]
    except KeyError:
        raise KeyError(
            f"Missing definition of environment variable {env_var} "
            f"needed when parsing configuration file"
        )


def joinPath(loader: Union[Loader, FullLoader, UnsafeLoader], node: Node) -> PathLike:
    """
    Join pieces of a file system path. Can be used as a custom tag handler.

    :param loader: YAML file loader
    :param node: YAML node
    :return: path
    :raises TypeError: if node is not a SequenceNode
    """
    if not isinstance(node, SequenceNode):
        raise TypeError("node input must be a SequenceNode")
    seq = loader.construct_sequence(node)
    return os.path.join(*seq)


# register tag handlers
add_implicit_resolver("!path", env_var_matcher)
add_constructor("!path", path_constructor)
add_constructor("!joinPath", joinPath)


def load_from_file(filename: PathLike) -> Configuration:
    """
    Load configuration reading given filename.

    :param filename: file to read
    :return: loaded configuration
    """
    try:
        return load(filename, safe_load=False, Loader=Loader)
    except TypeError:
        return load(filename)


def get_confs_in_path(path: PathLike, filename: str = "*.yml") -> Sequence[str]:
    """
    Retrieve all configuration files from system path, including the one in environment variable.

    :param path: path to search
    :param filename: filename can be either absolute (like /usr/src/Python-1.5/Makefile) or
        relative (like ../../Tools/*/*.gif), and can contain shell-style wildcards
    :return: list of retrieved configuration files paths
    """
    return [file for file in glob(os.path.join(path, filename))]


def merge_confs(
    filenames: Sequence[PathLike], default: Optional[str] = "defaults.yml"
) -> Configuration:
    """
    Merge configurations in given files.

    :param filenames: files to merge
    :param default: default configurations
    :return: merged configuration
    """
    lst = [default, *filenames] if default is not None else filenames
    print(f"Using Default Configuration file: {lst[0]}")
    return reduce(
        lambda config, fil: config.update(load_from_file(fil)),
        lst[1:],
        load_from_file(lst[0]),
    )
