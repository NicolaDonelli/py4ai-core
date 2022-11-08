"""Logging module."""
import os
import sys
from abc import ABC, abstractmethod
from importlib import import_module
from logging import FileHandler, Logger, captureWarnings, config, getLogger
from types import TracebackType
from typing import Any, Callable, List, Optional, Type, Union

from typing_extensions import Literal, TypedDict

from py4ai.core.config import merge_confs
from py4ai.core.types import PathLike

LevelTypes = Literal[
    "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET", 50, 40, 30, 20, 10, 0
]
StrLevelTypes = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


class LevelsDict(TypedDict):
    """Dictionary of logging levels."""

    CRITICAL: Literal[50]
    ERROR: Literal[40]
    WARNING: Literal[30]
    INFO: Literal[20]
    DEBUG: Literal[10]
    NOTSET: Literal[0]


DEFAULT_LOG_LEVEL: StrLevelTypes = "INFO"
levels = LevelsDict(CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0)


class WithLoggingABC(ABC):
    """Abstract class providing logging capabilities."""

    @property
    @abstractmethod
    def logger(self) -> Logger:
        """Logger instance to be used to output logs within a class."""
        raise NotImplementedError


class WithLogging(WithLoggingABC):
    """Base class to be used for providing a logger embedded in the class."""

    @property
    def logger(self) -> Logger:
        """
        Create logger.

        :return: default logger
        """
        nameLogger = str(self.__class__).replace("<class '", "").replace("'>", "")
        return getLogger(nameLogger)

    def logResult(
        self, msg: Union[Callable[..., str], str], level: StrLevelTypes = "INFO"
    ) -> Callable[..., Any]:
        """
        Return a decorator to allow logging of inputs/outputs.

        :param msg: message to log
        :param level: logging level
        :return: wrapped method
        """

        def wrap(x: Any) -> Any:
            if isinstance(msg, str):
                self.logger.log(levels[level], msg)
            else:
                self.logger.log(levels[level], msg(x))
            return x

        return wrap


def getDefaultLogger(level: LevelTypes = levels[DEFAULT_LOG_LEVEL]) -> Logger:
    """
    Create default logger.

    :param level: logging level
    :return: root logger
    """
    logger = getLogger()
    logger.setLevel(level)
    return logger


def configFromFiles(
    config_files: List[PathLike],
    capture_warnings: bool = True,
    catch_exceptions: Optional[str] = None,
) -> None:
    """
    Configure loggers from configuration obtained merging configuration files.

    If any handler inherits from FileHandler create the directory for its output files if it does not exist yet.

    :param config_files: list of configuration files. Configurations in files with larger list index
        overwrite corresponding configurations in files with smaller list index.
    :param capture_warnings: whether to capture warnings with logger
    :param catch_exceptions: name of the logger used to catch exceptions. If None do not catch exception with loggers.
    """
    captureWarnings(capture_warnings)

    configuration = merge_confs(filenames=config_files, default=None)
    for v in configuration.to_dict()["handlers"].values():
        splitted = v["class"].split(".")
        if issubclass(
            getattr(import_module(".".join(splitted[:-1])), splitted[-1]), FileHandler
        ):
            if not os.path.exists(os.path.dirname(v["filename"])):
                os.makedirs(os.path.dirname(v["filename"]))
    config.dictConfig(configuration)

    if catch_exceptions is not None:
        except_logger = getLogger(catch_exceptions)
        print(
            f"Catching exceptions with {except_logger.name} logger using handlers "
            f'{", ".join([x.name for x in except_logger.handlers if x.name is not None])}'
        )

        def handle_exception(
            exc_type: Type[BaseException],
            exc_value: BaseException,
            exc_traceback: Optional[TracebackType],
        ) -> Any:
            if issubclass(exc_type, KeyboardInterrupt) and exc_traceback is not None:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
            else:
                except_logger.error(
                    f"{exc_type.__name__}: {exc_value}",
                    exc_info=(exc_type, exc_value, exc_traceback),
                )

        sys.excepthook = handle_exception
