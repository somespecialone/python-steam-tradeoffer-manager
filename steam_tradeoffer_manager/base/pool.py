import asyncio
import logging
from typing import Callable, TypeVar, Generic, Iterator

from .abc import AbstractBasePool
from .exceptions import ConstraintException
from .mixins import PoolBotMixin
from .enums import ONCE_EVERY

__all__ = ("SteamBotPool",)

_log = logging.getLogger(__name__)
_B = TypeVar("_B", bound="_bot.SteamBot")
_I = TypeVar("_I")
_D = TypeVar("_D")  # not sure if this is working


class SteamBotPool(Generic[_I, _B], AbstractBasePool):
    """Steam bots pool"""

    # randomize time to sleep between restarting bots in pool instances of this class
    randomizer: Callable[[...], int] | None = ONCE_EVERY.FOUR_HOURS
    whitelist: set[int] | None = None  # whitelist with steam id's of admins/owners/etc
    domain: str = "steam.py"  # domain to register new api key

    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self._store: dict[_I, _B] = {}

    def startup(self):
        """Starting all bots"""
        tasks = [self.loop.create_task(bot.start(), name=f"{bot.id} start task") for bot in self]

        return asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    def add(self, bot: _B, raise_=True) -> None:
        """
        Add bot instance to pool
        :param bot: bot instance
        :param raise_: raise `ConstraintException` if bot in this pool or bounded to other pool. Default - `True`
        :return `None`
        :raises ConstraintException
        """
        if bot.pool:
            import warnings
            import inspect

            msg = f"Bot with id {bot.id} already in pool"

            if raise_:
                raise ConstraintException(msg)
            warnings.warn(msg, stacklevel=len(inspect.stack()) + 1)

        self._bind(bot)

    def remove(self, bot: _B) -> None:
        self._unbind(bot)

    def get(self, id: _I, default: _D = None) -> _B | _D | None:
        return self._store.get(id, default)

    def pop(self, id: _I) -> _B:
        """Unbind and return bot instance"""
        bot = self[id]
        self._unbind(bot)

        return bot

    async def shutdown(self) -> None:
        if tasks := [self.loop.create_task(bot.stop(), name=f"{bot.id} stop task") for bot in self]:
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    def _unbind(self, bot: _B) -> None:
        bot._pool = None
        del self._store[bot.id]

    def _bind(self, bot: _B) -> None:
        if not bot.id:
            raise ValueError(f"Bot id is {bot.id}")
        setattr(bot, "_pool", self)
        self._store[bot.id] = bot

    # container methods https://docs.python.org/3/reference/datamodel.html#emulating-container-types

    def __len__(self) -> int:
        return len(self._store)

    def __getitem__(self, id: _I) -> _B:
        return self._store[id]

    # Don't need as this method will add more complexity to binding process
    # def __setitem__(self, id: _I, bot: _BOT) -> None:
    #     if str(id) != str(bot.id):
    #         raise ConstraintException("Key and bot id must be the same")
    #
    #     self._bind(bot)
    #     self._storage[str(id)] = bot

    def __delitem__(self, id: _I) -> None:
        self._unbind(self[id])

    def __contains__(self, item: _I | _B) -> bool:
        if isinstance(item, PoolBotMixin):
            return item.id in self._store
        else:
            return item in self._store

    def __bool__(self) -> bool:
        return bool(self._store)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} len={len(self)}>"

    def __iter__(self) -> Iterator[_B]:
        return iter(self._store.values())


from . import bot as _bot
