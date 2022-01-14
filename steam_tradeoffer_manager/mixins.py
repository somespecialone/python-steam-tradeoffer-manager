import logging
import asyncio
import datetime
from typing import TypeAlias, Coroutine, Any, Callable, TYPE_CHECKING

import steam
from steam.gateway import Msg, MsgProto

__all__ = ("ManagerDispatchMixin",)

_log = logging.getLogger(__name__)
EventType: TypeAlias = "Callable[..., Coroutine[Any, Any, Any]]"


class ManagerDispatchMixin:
    loop: asyncio.AbstractEventLoop

    @property
    def errors(self) -> list[Exception]:
        return getattr(self, "_errors", [])

    # TODO: i sure i forgot smth there
    async def on_error(self, event: str, error: Exception, *args, **kwargs):
        if errors := getattr(self, "_errors", None):
            errors.append(error)
        else:
            setattr(self, "_errors", [error])
        _log.error(f"Ignoring manager exception in {event}")

    def _schedule_event(self, coro: EventType, event_name: str, *args, **kwargs) -> asyncio.Task:
        async def _run_event() -> None:
            try:
                await coro(*args, **kwargs)
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                try:
                    await self.on_error(event_name, exc, *args, **kwargs)
                except asyncio.CancelledError:
                    pass

        return self.loop.create_task(_run_event(), name=f"{event_name} task")

    # https://github.com/Gobot1234/steam.py/blob/main/steam/client.py#L279
    def dispatch(self, bot, event: str, *args, **kwargs) -> None:
        _log.debug(f"{bot!r} dispatched event {event}")
        method = f"on_{event}"

        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._schedule_event(coro, method, bot, *args, **kwargs)

    if TYPE_CHECKING:  # pragma: no cover
        from .offer import ManagerTradeOffer
        from .inventory import BotInventory

        # manager events
        async def on_close_trade_offer(self, bot, trade: ManagerTradeOffer) -> None:
            """
            Calls when `ManagerTradeOffer` was closed
            (decline/accept by partner, expires or cancelled by timeout).
            :param bot: bot instance who's sent signal
            :param trade: `ManagerTradeOffer` that was closed
            :return: None
            """

        async def on_manager_trade_send(self, bot, trade: ManagerTradeOffer) -> None:
            """
            Calls when bot send `ManagerTradeOffer` offer.
            :param bot: bot instance who's sent signal
            :param trade: `ManagerTradeOffer` that was closed
            :return: None
            """

        async def on_inventory_update(self, bot, inventory: BotInventory) -> None:
            """
            Calls when bot update/fetch their inventory.
            :param bot: bot instance who's sent signal
            :param inventory: `steam.Game` inventory
            :return: None
            """

        # steamio events
        async def on_connect(self, bot) -> None: ...

        async def on_disconnect(self, bot) -> None: ...

        async def on_ready(self, bot) -> None: ...

        async def on_login(self, bot) -> None: ...

        async def on_logout(self, bot) -> None: ...

        async def on_message(self, bot, message: steam.Message) -> None: ...

        async def on_typing(self, bot, user: steam.User, when: datetime.datetime) -> None: ...

        async def on_trade_receive(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_send(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_accept(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_decline(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_cancel(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_expire(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_trade_counter(self, bot, trade: steam.TradeOffer) -> None: ...

        async def on_comment(self, bot, comment: steam.Comment) -> None: ...

        async def on_user_invite(self, bot, invite: steam.UserInvite) -> None: ...

        async def on_user_invite_accept(self, bot, invite: steam.UserInvite) -> None: ...

        async def on_user_invite_decline(self, bot, invite: steam.UserInvite) -> None: ...

        async def on_user_update(self, bot, before: steam.User, after: steam.User) -> None: ...

        async def on_user_remove(self, bot, user: steam.User) -> None: ...

        async def on_clan_invite(self, bot, invite: steam.ClanInvite) -> None: ...

        async def on_clan_invite_accept(self, bot, invite: steam.ClanInvite) -> None: ...

        async def on_clan_invite_decline(self, bot, invite: steam.ClanInvite) -> None: ...

        async def on_clan_join(self, bot, clan: steam.Clan) -> None: ...

        async def on_clan_update(self, bot, before: steam.Clan, after: steam.Clan) -> None: ...

        async def on_clan_leave(self, bot, clan: steam.Clan) -> None: ...

        async def on_group_join(self, bot, group: steam.Group) -> None: ...

        async def on_group_update(self, bot, before: steam.Group, after: steam.Group) -> None: ...

        async def on_group_leave(self, bot, group: steam.Group) -> None: ...

        async def on_event_create(self, bot, event: steam.Event) -> None: ...

        async def on_announcement_create(self, bot, announcement: steam.Announcement) -> None: ...

        async def on_socket_receive(self, bot, msg: Msg | MsgProto) -> None: ...

        async def on_socket_send(self, bot, msg: Msg | MsgProto) -> None: ...
