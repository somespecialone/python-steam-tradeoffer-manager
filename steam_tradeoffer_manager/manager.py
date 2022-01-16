import logging
from typing import TypeVar
from datetime import timedelta

from steam import Item, User, Game

from .base import SteamBotPool, ONCE_EVERY
from .mixins import ManagerDispatchMixin
from .offer import ManagerTradeOffer
from .trades import ManagerTrades
from .inventory import BotInventory
from .item import BotItem
from .items import ManagerItems
from .utils import parse_trade_url, join_multiple_in_string

__all__ = ("TradeOfferManager",)

_log = logging.getLogger(__name__)
_B = TypeVar("_B", bound="bot.ManagerBot")
_I = TypeVar("_I", bound=int)


class TradeOfferManager(SteamBotPool[_I, _B], ManagerDispatchMixin):
    """Manager class..."""
    randomizer = ONCE_EVERY.SIX_HOURS
    offer_cancel_delay: timedelta | None = timedelta(minutes=5)
    prefetch_games: tuple[Game] = ()

    def __init__(self):
        super().__init__()
        self.trades: ManagerTrades["TradeOfferManager"] = ManagerTrades(self)
        self.items: ManagerItems["TradeOfferManager", _B] = ManagerItems(self)

    def get_offer(self, id: int) -> ManagerTradeOffer[_B] | None:
        """
        Get `ManagerTradeOffer` from trades.
        Similar to `.trades.get(id)`.
        """
        return self.trades.get(id)

    def _create_offer(
            self,
            bot: _B,
            partner: User,
            token: str | None,
            message: str | None,
            send_items: list[BotItem] | None,
            receive_items: list[Item] | None,
    ) -> ManagerTradeOffer[_B]:
        if bot not in self: raise ValueError(f"Bot {bot.user} not bounded to this manager")

        return bot.create_offer(
            partner=partner,
            token=token,
            message=message,
            send_items=send_items,
            receive_items=receive_items
        )

    def _create_offers(
            self,
            owners: set[_B],
            partner: User,
            token: str | None,
            message: str | None,
            send_items: list[BotItem] | None,
            receive_items: list[Item] | None,
            msg_in_all_offers: bool
    ) -> list[ManagerTradeOffer[_B]]:
        trades: list[ManagerTradeOffer[_B]] = []

        receive_items_flag = False
        message_flag = False
        for bot in owners:
            trades.append(
                self._create_offer(
                    bot=bot,
                    partner=partner,
                    token=token,
                    message=message if (not message_flag or msg_in_all_offers) else None,
                    send_items=[item for item in send_items if item.owner is bot],
                    receive_items=receive_items if not receive_items_flag else None
                )
            )
            receive_items_flag = True
            message_flag = True

        return trades

    def create_offer(
            self,
            partner: User,
            token: str | None = None,
            message: str | None = None,
            send_items: list[BotItem] | None = None,
            receive_items: list[Item] | None = None,
    ) -> ManagerTradeOffer[_B]:
        """
        Create `ManagerTradeOffer`. Consider that items must be owned by one bot.
        :param partner: `steam.User` to whom trade offers will be sent
        :param token: trade token of user if user not in friends list
        :param message: text that be applied to trade offer
        :param send_items: items that will be sent within trade offer
        :param receive_items: items that will be received within trade offer
        :return: `ManagerTradeOffer`
        :raises ValueError if items belong to two or more manager bots.
                ValueError - if bot not bounded to this manager
        """
        owner = {item.owner for item in send_items}
        f = join_multiple_in_string(tuple(owner))
        if len(owner) > 1: raise ValueError(f"Items to send owns by few or more manager bots {f}")

        return self._create_offer(
            bot=owner.pop(),
            partner=partner,
            token=token,
            message=message,
            send_items=send_items,
            receive_items=receive_items
        )

    async def create_offer_from_url(
            self,
            trade_url: str,
            message: str | None = None,
            send_items: list[BotItem] | None = None,
            receive_items: list[Item] | None = None,
    ) -> ManagerTradeOffer[_B]:
        """
        Create `ManagerTradeOffer` from trade url. Requires fetching user model.
        Consider that items must be owned by one bot.
        :param trade_url: trade url of user
        :param message: text that be applied to trade offer
        :param send_items: items that will be sent within trade offer
        :param receive_items: items that will be received within trade offer
        :return: `ManagerTradeOffer`
        :raises ValueError if items belong to two or more manager bots
        """
        owner = {item.owner for item in send_items}
        f = join_multiple_in_string(tuple(owner))
        if len(owner) > 1: raise ValueError(f"Items to send owns by few or more manager bots {f}")

        bot: _B = owner.pop()
        partner_id32, token = parse_trade_url(trade_url)
        partner = bot.get_user(partner_id32) or await bot.fetch_user(partner_id32)

        return self._create_offer(
            bot=bot,
            partner=partner,
            token=token,
            message=message,
            send_items=send_items,
            receive_items=receive_items
        )

    def create_offers(
            self,
            partner: User,
            token: str | None = None,
            message: str | None = None,
            send_items: list[BotItem] | None = None,
            receive_items: list[Item] | None = None,
            *,
            msg_in_all_offers: bool = False
    ) -> list[ManagerTradeOffer[_B]]:
        """
        Creates different trade offers if items placed in different bots inventories.
        Consider that if token not passed user must be in friends list of all bots.
        Received items will be applied to first trade offer.
        :param partner: `steam.User` to whom trade offers will be sent
        :param token: trade token of user if user not in friends list
        :param message: text that be applied to trade offer
        :param send_items: items that will be sent within trade offer
        :param receive_items: items that will be received within trade offer
        :param msg_in_all_offers: if `True` send message duplicates in all offers
        :return: list[`ManagerTradeOffer`]
        """
        owners: set[_B] = {item.owner for item in send_items}

        return self._create_offers(
            owners=owners,
            partner=partner,
            token=token,
            message=message,
            send_items=send_items,
            receive_items=receive_items,
            msg_in_all_offers=msg_in_all_offers
        )

    async def create_offers_from_url(
            self,
            trade_url: str,
            message: str | None = None,
            send_items: list[BotItem] | None = None,
            receive_items: list[Item] | None = None,
            *,
            msg_in_all_offers: bool = False
    ) -> list[ManagerTradeOffer[_B]]:
        """
        Creates different trade offers from trade url if items placed in different bots inventories.
        Requires fetching user model.
        Consider that if token not passed user must be in friends list of all bots.
        Received items will be applied to first trade offer.
        :param trade_url: trade url of user
        :param message: text that be applied to trade offer
        :param send_items: items that will be sent within trade offer
        :param receive_items: items that will be received within trade offer
        :param msg_in_all_offers: if `True` send message duplicates in all offers
        :return: list[`ManagerTradeOffer`]
        """
        partner_id32, token = parse_trade_url(trade_url)

        owners: set[_B] = {item.owner for item in send_items}
        bot = owners.pop()
        partner = bot.get_user(partner_id32) or await bot.fetch_user(partner_id32)
        owners.add(bot)

        return self._create_offers(
            owners=owners,
            partner=partner,
            token=token,
            message=message,
            send_items=send_items,
            receive_items=receive_items,
            msg_in_all_offers=msg_in_all_offers
        )

    async def on_inventory_update(self, bot: _B, inventory: BotInventory) -> None:
        for item in inventory: self.items.add(item)

    async def on_manager_trade_send(self, bot: _B, trade: ManagerTradeOffer) -> None:
        self.trades.add(trade)


from . import bot
