import asyncio
import logging
from typing import Any, TypeVar, Callable, Coroutine

import steam
from aiohttp import BasicAuth, BaseConnector

from .enums import BotState
from .mixins import PoolBotMixin

__all__ = ('SteamBot',)

_log = logging.getLogger(__name__)
_P = TypeVar("_P", bound='pool.SteamBotPool')
_I = TypeVar("_I", bound=int)


class SteamBot(steam.Client, PoolBotMixin[_I, _P]):
    """
    Simple steam bot.
    `id` attr must be steam id64
    """

    constraints = ('username',)
    dimension = 'steam'

    def __init__(
            self,
            username: str,
            password: str,
            shared_secret: str,
            identity_secret: str,
            *,
            id: _I = None,
            whitelist: set[int] | None = None,
            user_agent: str | None = None,
            proxy: str | None = None,
            proxy_auth: BasicAuth | None = None,
            connector: BaseConnector | None = None,
            randomizer: Callable[[], int] | None = None,
            domain: str | None = None,
            **options: Any,
    ) -> None:
        self._id = id

        super().__init__(proxy=proxy, proxy_auth=proxy_auth, connector=connector, **options)

        # as in Client.start method
        self.username = username
        self.password = password
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret

        if user_agent:
            self.http.user_agent = user_agent

        self._running_task: asyncio.Task | None = None
        self._refresh_task: asyncio.Task | None = None

        self._errors: list[Exception] = []
        self._state: BotState = BotState.Stopped
        self._randomizer = randomizer
        self._whitelist = whitelist
        self._domain = domain

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return getattr(self.pool, "loop", self._loop)

    # setter for steam.Client.__init__
    @loop.setter
    def loop(self, _):
        self._loop = asyncio.get_event_loop()

    @property
    def state(self) -> BotState:
        return self._state

    @property
    def domain(self) -> str:
        try:
            return self._domain or self.pool.domain
        except AttributeError:  # if bot don't bound to pool and self domain is None
            return "steam.py"

    @domain.setter
    def domain(self, value: str | None):
        self._domain = value

    @property
    def whitelist(self) -> set[int] | None:
        try:
            return self._whitelist or self.pool.whitelist
        except AttributeError:  # if bot don't bound to pool and self whitelist is None
            return None

    @whitelist.setter
    def whitelist(self, value: set[int]):
        self._whitelist = value

    @property
    def api_key(self) -> str | None:
        return self.http.api_key

    async def _start(self) -> None:
        _log.debug(f"Attempting to start bot {self.id}")
        try:
            self._state = BotState.Waiting
            await self.login(self.username, self.password, shared_secret=self.shared_secret)
            await self.connect()

        except steam.InvalidCredentials as e:
            self._errors.append(e)
            self._state = BotState.InvalidCredentials
            _log.error(f"Invalid credentials for {self.id}")

        except (steam.NoCMsFound, steam.LoginError, Exception) as e:
            self._errors.append(e)
            self._state = BotState.UnknownError
            _log.exception(f"Error while starting bot {self.id}", stack_info=True, exc_info=e)

        else:
            self._state = BotState.Stopped
            _log.info(f"Bot {self} is stopped")

        finally:  # ensure that bot has to be closed/stopped
            if not self.is_closed():
                await self.close()

    async def start(self, *, timeout: int = 60) -> None:
        """Starts bot in separate task and wait until he is ready.
        :param timeout: amount of seconds to wait for ready,
        return after `timeout` passes or bot dispatched `ready`.
        """
        self._running_task = self.loop.create_task(self._start(), name=f"{self.user}-bot running task")
        try:
            await self.wait_for("ready", timeout=timeout)
            if self.randomizer is not None:
                self._refresh_task = self.loop.create_task(
                    self._restarter(),
                    name=f"{self.user}-bot refresh task"
                )

        except asyncio.TimeoutError:
            _log.warning(f"Timeout has been reached for {self.id}")

    async def _restarter(self):
        await self.wait_until_ready()

        while not self.is_closed():
            await asyncio.sleep(self.randomizer())
            await self.restart()

            await self.wait_until_ready()

    async def restart(self) -> None:
        """Stop, clear all inner cache and then start bot"""
        await self.stop()
        await self.start()

    @property
    def randomizer(self) -> Callable[[], int] | None:
        try:
            return self._randomizer or self.pool.randomizer
        except AttributeError:  # if bot don't bounded to pool
            return None

    @randomizer.setter
    def randomizer(self, value: Callable[[], int]):
        self._randomizer = value

    async def on_ready(self) -> None:
        self._state = BotState.Active
        if not self.id: setattr(self, "_id", self.user.id64)  # id will be automatically set when client is ready

        _log.info(f"Bot {self.user} is ready")

    async def on_error(self, event: str, error: Exception, *args, **kwargs):
        self._errors.append(error)
        _log.error(f"Bot {self.user} ignore exception in {event}", exc_info=error)

    @property
    def errors(self) -> list[Exception]:
        # maybe there should be logic in future
        return self._errors

    def stop(self):
        """Stop serving"""
        # if not self.is_closed():  # fix for accounts that doesn't have api key
        #     self.user.flags = []

        return super().close()

    def close(self) -> Coroutine[Any, Any, None]:
        """Similar to `.stop()` method call"""
        return self.stop()

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} user={self.user.__repr__() if self.user else None}>"

    def __del__(self):
        if not self.is_closed():
            import warnings

            warnings.warn(f'Unstopped bot {self}!', ResourceWarning, source=self)
            self._refresh_task.cancel()
            # maybe asyncio.call_exception_handler needed
        if self.pool: del self.pool[self.id]
        super().__del__()

    def __str__(self) -> str:
        return self.user.name if self.user else (str(self.id) or self.username)

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: "SteamBot") -> bool:
        return self.id == other.id


from . import pool
