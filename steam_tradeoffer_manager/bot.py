import logging
from typing import TypeVar, Callable, Any, TypeAlias, overload
from datetime import timedelta

import steam
from aiohttp import BasicAuth, BaseConnector

from .base import SteamBot
from .item import BotItem
from .offer import ManagerTradeOffer
from .inventory import GamesInventory
from .trades import ManagerBotTrades
from .utils import parse_trade_url, ready_required, copy_user

__all__ = ("ManagerBot",)

_log = logging.getLogger(__name__)
_M = TypeVar("_M", bound="manager.TradeOfferManager")
_I = TypeVar("_I", bound=int)
SteamGame: TypeAlias = "steam.Game | steam.trade.StatefulGame"


class ManagerBot(SteamBot[_I, _M]):
    """
    Bot class specially for manager.
    :param username: The username of the user's account.
    :param password: The password of the user's account.
    :param shared_secret: The shared_secret of the desired Steam account, used to generate the 2FA code for login.
        If `None` is passed, the code will need to be inputted by the user via :meth:`code`.
    :param identity_secret: The identity secret for the account to log in to.
    :param id: Optional, but required for add bot to manager. Must be steam id64.
        If not passed - bot set it himself when ready dispatched.
    :param whitelist: Set of steam id64 (int), trade offers from bot will automatically accept.
    :param user_agent: User agent that will be passed to :class:`aiohttp.ClientSession`.
    :param proxy: A proxy URL to use for requests.
    :param proxy_auth: The proxy authentication to use with requests.
    :param connector: The connector to use with the :class:`aiohttp.ClientSession`.
    :param randomizer: Callback that randomize time between restarts.
    :param domain: Domain name to register api key for. Defaults - `Manager.domain` is "steam.py"
    :param offer_cancel_delay: Time for auto cancel own sent trade offer.
    :param prefetch_games: Tuple of `steam.Game` which will be fetched when bot client is ready.
    :param max_messages: The maximum number of messages to store in the internal cache, default is 1000.
    :param game: A games to set your status as on connect.
    :param games: A list of games to set your status to on connect.
    :param state: The state to show your account as on connect.
        Setting your status to :attr:`~steam.PersonaState.Offline`, will stop you receiving persona state updates
        and by extension :meth:`on_user_update` will stop being dispatched.
    :param ui_mode: The UI mode to set your status to on connect.
    :param flags: Flags to set your persona state to.
    :param force_kick: Whether to forcefully kick any other playing sessions on connect. Defaults to `False`.
    """

    @overload
    def __init__(self,
                 username: str,
                 password: str,
                 shared_secret: str,
                 identity_secret: str,
                 *,
                 id: int = None,
                 whitelist: set[int] | None = None,
                 user_agent: str | None = None,
                 proxy: str | None = None,
                 proxy_auth: BasicAuth | None = None,
                 connector: BaseConnector | None = None,
                 randomizer: Callable[[], int] | None = None,
                 domain: str | None = None,
                 offer_cancel_delay: timedelta | None = None,
                 prefetch_games: tuple[SteamGame] = (),
                 max_messages: int | None = ...,
                 game: steam.Game | None = ...,
                 games: list[steam.Game] = ...,
                 state: steam.PersonaState | None = ...,
                 ui_mode: steam.UIMode | None = ...,
                 flags: steam.PersonaStateFlag | None = ...,
                 force_kick: bool = ...,
                 ): ...

    def __init__(
            self,
            username: str,
            password: str,
            shared_secret: str,
            identity_secret: str,
            *,
            offer_cancel_delay: timedelta | None = None,
            prefetch_games: tuple[SteamGame] = (),
            **kwargs
    ):
        super().__init__(username, password, shared_secret, identity_secret, **kwargs)

        self._offer_cancel_delay = offer_cancel_delay
        self._trade_url_token: str | None = None
        self._prefetch_games = prefetch_games

        self.inventory: GamesInventory["ManagerBot"] = GamesInventory(self)
        self.manager_trades: ManagerBotTrades["ManagerBot"] = ManagerBotTrades(self)

    @property
    def manager(self) -> _M | None:
        """Same as .pool"""
        return self.pool

    @property
    def offer_cancel_delay(self) -> timedelta | None:
        try:
            return self._offer_cancel_delay or self.manager.offer_cancel_delay
        except AttributeError:  # if bot don't bound to manager and self offer_cancel_delay is None
            return None

    @property
    def prefetch_games(self) -> tuple[SteamGame]:
        try:
            return self._prefetch_games or self.manager.prefetch_games
        except AttributeError:  # if bot don't bound to manager and self prefetch_games is None
            return tuple()

    @prefetch_games.setter
    def prefetch_games(self, value: tuple[SteamGame]):
        self._prefetch_games = value

    @offer_cancel_delay.setter
    def offer_cancel_delay(self, value: timedelta | None):
        self._offer_cancel_delay = value

    @property
    def trade_url(self) -> str | None:
        if self._trade_url_token:
            return f"https://steamcommunity.com/tradeoffer/new/?partner={self.user.id}&token={self._trade_url_token}"

    @ready_required
    def generate_trade_url(self):
        """
        Generate new trade url, previous be revoked.
        :return: New trade url
        """
        return super().trade_url(generate_new=True)

    @ready_required
    def get_all_items(self) -> list[BotItem]:
        """Similar to `.inventory.items`"""
        return self.inventory.items

    @ready_required
    def create_offer(
            self,
            partner: steam.User,
            token: str | None = None,
            message: str | None = None,
            send_items: list[steam.Item] | None = None,
            receive_items: list[steam.Item] | None = None,
    ) -> ManagerTradeOffer["ManagerBot"]:
        """
        Create trade offer model, but not send it.
        :param partner: `steam.User` instance to whom offer will be sent
        :param message: message applied to trade offer
        :param token: token from trade url if `partner` not in friends list
        :param send_items: list of items/assets to send `partner`
        :param receive_items: list of items/assets to receive from `partner`
        :return: `ManagerTradeOffer` model
        """
        return ManagerTradeOffer(
            _steam_offer=steam.TradeOffer(
                message=message,
                token=token,
                items_to_send=send_items,
                items_to_receive=receive_items),
            owner=self,
            partner=copy_user(self, partner) if partner.id64 not in self._connection._users else partner
        )

    @ready_required
    async def create_offer_from_trade_url(
            self,
            trade_url: str,
            message: str | None = None,
            send_items: list[steam.Item] | None = None,
            receive_items: list[steam.Item] | None = None,
    ) -> ManagerTradeOffer["ManagerBot"]:
        """
        Create trade offer model using trade url, but not send it.
        May require fetch `steam.User`.
        :param trade_url: trade url of the user whom offer will be sent
        :param message: message applied to trade offer
        :param send_items: list of items/assets to send `partner`
        :param receive_items: list of items/assets to receive from `partner`
        :return: `ManagerTradeOffer` model
        """
        partner_id32, token = parse_trade_url(trade_url)
        partner = self.get_user(partner_id32) or await self.fetch_user(partner_id32)

        return self.create_offer(
            partner,
            token,
            message,
            send_items,
            receive_items
        )

    @ready_required
    def get_trade(self, id: int):
        """
        Get default steam trade offer from cache.
        :param id: id – The id of the trade to search for from the cache.
        """
        return super().get_trade(id)

    def get_manager_trade(self, id: int) -> ManagerTradeOffer["ManagerBot"] | None:
        """Return `ManagerTradeOffer`. Same as `.manager_trades.get()`"""
        return self.manager_trades.get(id)

    @ready_required
    def fetch_trade(self, id: int):
        """
        Fetch and return default steam trade offer.
        :param id: The ID of the trade to search for from the API
        """
        return super().fetch_trade(id)

    @ready_required
    async def send_offer(self, offer: ManagerTradeOffer) -> None:
        if offer.owner is self:
            await offer.partner.send(trade=offer._steam_offer)
            self.manager_trades.add(offer)
            if offer.cancel_delay is not None: offer._set_cancel_timeout()

            # TODO: check if this is necessary
            self.loop.create_task(self.ws._connection.poll_trades(), name=f"{self.user} poll trades task")

            self.dispatch_to_manager("manager_trade_send", offer)
        else:
            raise ValueError(f"Cannot send trade. Owner of this offer {offer.id} is {offer.owner}-bot")

    async def on_trade_receive(self, trade: steam.TradeOffer) -> None:
        """
        Fetches and save inventories when receives trade offer from user in whitelist.
        """
        if trade.partner.id64 in (self.whitelist or ()):
            await trade.accept()
            fetched = set()
            for item in trade.items_to_receive:
                if item.game.name not in fetched and item.game.id not in fetched:
                    await self.inventory.fetch_game_inventory(item.game)
                    fetched.add(item.game.name or item.game.id)

    def _close_trade_offer(self, trade: steam.TradeOffer):
        if trade.is_our_offer():  # there safe to call is_our_offer
            if trade.id in self.manager_trades:
                manager_trade_offer = self.manager_trades.pop(trade.id)  # remove manager trade offer from trades
                manager_trade_offer._steam_offer = trade  # ensure that offer instance is updated
                if manager_trade_offer._cancel_delay_timer:
                    manager_trade_offer._cancel_delay_timer.cancel()

                # manager_trade_offer.state_event.set()

                self.dispatch_to_manager("close_trade_offer", manager_trade_offer)
            else:
                _log.error(f"Manager trade offer {trade.id} not in trades")

    # handle offers
    async def on_trade_decline(self, trade: steam.TradeOffer):
        self._close_trade_offer(trade)

    async def on_trade_accept(self, trade: steam.TradeOffer):
        self._close_trade_offer(trade)

    async def on_trade_cancel(self, trade: steam.TradeOffer):
        self._close_trade_offer(trade)

    async def on_trade_expire(self, trade: steam.TradeOffer):
        self._close_trade_offer(trade)

    async def on_ready(self) -> None:
        await super().on_ready()

        if not self._trade_url_token:
            trade_url = await super().trade_url()
            _, self._trade_url_token = parse_trade_url(trade_url)

        for game in self.prefetch_games: await self.inventory.fetch_game_inventory(game)  # fetch inventories

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        super().dispatch(event, *args, **kwargs)
        self.dispatch_to_manager(event, *args, **kwargs)

    def dispatch_to_manager(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatch event to manager."""
        if self.manager:
            try:
                self.manager.dispatch(self, event, *args, **kwargs)
            except AttributeError:
                pass


from . import manager
