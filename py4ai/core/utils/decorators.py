"""Module that gathers useful decorators."""

import os
from functools import wraps
from glob import glob
from typing import Any, Callable, Iterable, Tuple, TypeVar

import pandas as pd

from py4ai.core.types import PathLike, T
from py4ai.core.utils.fs import create_dir_if_not_exists

A = TypeVar("A")
B = TypeVar("B")


def cache(func: Callable[..., T]) -> Callable[..., T]:
    """
    Return a decorator to cache function return values.

    :param func: input function
    :return: function wrapper
    """

    @wraps(func)
    def _wrap(obj):
        try:
            return obj.__dict__[func.__name__]
        except KeyError:
            score = func(obj)
            obj.__dict__[func.__name__] = score
            return score

    _wrap.__name__ = func.__name__
    return _wrap


def lazyproperty(obj: Any) -> property:
    """
    Return a lazy property, i.e. a property that is computed if needed and then cached.

    :param obj: method do decorate
    :return: wrapped method
    """
    return property(cache(obj))


class Cached(object):
    """Class to cache results and export them as pickle to be later reloaded."""

    @property
    def _cache(self):
        """
        Hidden property that stores the custom cache that can be exported and imported.

        :return: cached data
        """
        try:
            return self._cache_data
        except AttributeError:
            self._cache_data = {}
            return self._cache

    @staticmethod
    def cache(func: Callable[["Cached"], T]) -> property:
        """
        Return a decorator to cache function return values.

        :param func: input function
        :return: function wrapper
        """

        @wraps(func)
        def _wrap(obj: "Cached"):
            try:
                return obj._cache[func.__name__]
            except KeyError:
                score = func(obj)
                obj._cache[func.__name__] = score
                return score

        return property(_wrap)

    def clear_cache(self) -> None:
        """Clear cache of the object."""
        self._cache.clear()

    def save_pickles(self, path: PathLike) -> None:
        """
        Save pickle in given path.

        :param path: saving path
        """
        path = create_dir_if_not_exists(path)

        for k, data in self._cache.items():
            Cached.save_element(os.path.join(path, k), data)

    @staticmethod
    def save_element(filename: PathLike, obj: Any) -> None:
        """
        Save given object in given file.

        :param filename: saving path
        :param obj: object to be saved
        :raises Exception: if any error occurs while saving the file
        """
        if isinstance(obj, dict):
            create_dir_if_not_exists(filename)
            [Cached.save_element(os.path.join(filename, k), v) for k, v in obj.items()]
        elif isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series):
            pd.to_pickle(obj, "%s.p" % filename)
        else:
            try:
                pd.to_pickle(obj, "%s.p" % filename)
            except Exception as ex:
                raise type(ex)("Cannot save input of type %s" % str(obj.__class__))

    def load(self, filename: PathLike) -> None:
        """
        Load pickle at given path (or all pickles in given folder).

        :param filename: path to pickles
        """
        self._cache.update(dict(self.load_element(filename, "")))

    @classmethod
    def load_element(
        cls, filename: PathLike, prefix: str = ""
    ) -> Iterable[Tuple[PathLike, Any]]:
        """
        Load given element/property of the object.

        :param filename: name of the file/directory where the data should be taken from
        :param prefix: prefix to add to elements in filename in case it is a directory
        :yield: iterable of couples (path, loaded object)
        """
        if os.path.isdir(filename):
            for path in glob(os.path.join(filename, "*")):
                for name, obj in cls.load_element(
                    path, f"{cls._reformat_name(filename)}_"
                ):
                    yield f"{prefix}{name}", obj
        else:
            yield str(cls._reformat_name(filename)), pd.read_pickle(filename)

    @staticmethod
    def _reformat_name(filename: PathLike) -> PathLike:
        """
        Reformat file name to make it readable with load_element.

        :param filename: file name to reformat
        :return: reformatted filename
        """
        if os.path.isfile(filename):
            return os.path.basename(filename).replace(".p", "")
        else:
            return os.path.basename(filename)


def same_type(f: Callable[[A, B], T]) -> Callable[[A, B], T]:
    """
    Check that both arguments of input function have the same type.

    :param f: function
    :return: function
    """

    @wraps(f)
    def new_f(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(
                f"other's type ({type(other)}) is different from self's type ({type(self)})"
            )
        return f(self, other)

    return new_f
