import inspect
import logging
from typing import TypeVar, Generic, Hashable, Sequence, Final

from .abc import AbstractBasePool
from .exceptions import ConstraintException
from ..utils import join_multiple_in_string

__all__ = ('PoolBotMixin', 'ConstraintsMixin')

_log = logging.getLogger(__name__)
_P = TypeVar("_P", bound=AbstractBasePool)
_I = TypeVar('_I')


class ConstraintsMixin:
    """
    Mixin preventing create new object that violates unique constraint fields.
    Constraint fields not necessary need to be attributes on model,
    but always must be passed like arguments to `__init__` and be `hashable`.
    Implement `__del__` method to clean up hashes in storage while garbage collecting,
    """
    __storage__: Final[dict[str, set[int]]] = {}

    constraints: Sequence[str | Sequence[str]] = ()
    dimension: str

    def __init_subclass__(cls, dimension: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        subclass_dimension = getattr(cls, 'dimension', None)
        arg_dimension = dimension
        if subclass_dimension and arg_dimension:
            import warnings

            warnings.warn('Subclass overrides `dimension` and `dimension` arg has been passed to subclass init. '
                          f'Used [{subclass_dimension}] by default.', stacklevel=len(inspect.stack()) + 1)

        if subclass_dimension:
            cls.dimension = subclass_dimension
        elif arg_dimension:
            cls.dimension = arg_dimension
        else:
            cls.dimension = cls.__name__

        cls.__storage__.update({cls.dimension: set()})  # init storage

    def __new__(cls, *args, **kwargs):
        # ensure that all args will be transferred to super().__new__ method of parent if he needs them
        try:
            __instance = super().__new__(cls)
        except TypeError:
            __instance = super().__new__(cls, *args, **kwargs)

        __init_args = tuple(inspect.signature(cls.__init__).parameters)[1:]  # getting init arguments
        __merged_args: dict[str, Hashable] = {**{t[0]: t[1] for t in zip(__init_args, args)}, **kwargs}
        __instance._hashes = cls._collect_hashes(__merged_args)

        __instance._check_constraints()
        return __instance

    @classmethod
    def _collect_hashes(cls, merged_args: dict[str, Hashable]) -> tuple[int]:
        hashes = []
        for const in cls.constraints:
            if isinstance(const, str):
                h = hash(merged_args[const])
            else:
                h = []
                for const1 in const:
                    h.append(hash(merged_args[const1]))
                h = hash(tuple(h))
            hashes.append(h)

        return tuple(hashes)

    def _check_constraints(self):
        for h in self._hashes:
            if h in self.__storage__[self.dimension]:
                f = join_multiple_in_string(self.constraints)
                # would be great if I write violated constraints here
                raise ConstraintException(f'Instance with unique values({f}) already created.')

        self.__storage__[self.dimension].update(self._hashes)

    def __del__(self) -> None:
        self.__storage__[self.dimension].difference_update(self._hashes)  # clean up hashes while garbage collecting


class _MappingPoolBotMixin(ConstraintsMixin, Generic[_I, _P]):
    """Mixin for bot. Contains required methods to interact with pool"""
    # maps to ids and pool
    __ids__: Final[dict[str, _I]] = {}
    __pools__: Final[dict[str, _P]] = {}

    @property
    def id(self) -> _I | None:
        return self.__ids__.get(str(id(self)))

    # @id.setter
    # def id(self, value: _I):
    #     self.__ids__[str(id(self))] = value

    @property
    def pool(self) -> _P | None:
        return self.__pools__.get(str(id(self)))

    # @pool.setter
    # def pool(self, value: _M):
    #     self.__pools__[str(id(self))] = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


class _PropertyPoolBotMixin(ConstraintsMixin, Generic[_I, _P]):
    """Mixin for bot. Contains required methods to interact with pool"""

    # pure properties
    @property
    def id(self) -> _I | None:
        return getattr(self, '_id', None)

    @property
    def pool(self) -> _P | None:
        return getattr(self, '_pool', None)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


# deprecated
class _MagickPoolBotMixin(ConstraintsMixin, Generic[_I, _P]):
    """Mixin for bot. Contains required methods to interact with pool"""

    # some magic to add id attr to instance
    def __new__(cls, *args, **kwargs):
        _instance = super().__new__(*args, **kwargs)
        _id: _I | None = None
        _pool: _P | None = None
        _instance.id = _id
        _instance.pool = _pool
        return _instance

    # call __init__ of parent even if mixin __init__ will be called
    # and called first by MRO(stands first in subclasses)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"


PoolBotMixin = _PropertyPoolBotMixin
