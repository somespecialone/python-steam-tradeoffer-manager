import asyncio
from dataclasses import dataclass
from typing import Coroutine, Any, Generic, TypeVar, TypeAlias
from datetime import timedelta

from steam import TradeOffer, User, TradeOfferState

__all__ = ("ManagerTradeOffer",)

_B = TypeVar("_B", bound="bot.ManagerBot")
TradeOfferAlias: TypeAlias = "ManagerTradeOffer | TradeOffer"  # specially for __eq__


@dataclass(eq=False)
class ManagerTradeOffer(Generic[_B]):
    """
    Wraps `steam."ManagerTradeOffer"` class only for offers that active and owns by TradeOfferManager bots.
    """

    _steam_offer: TradeOffer
    owner: _B
    partner: User | None

    _cancel_delay: timedelta | None = None
    _cancel_delay_timer: asyncio.Task | None = None

    # _state_event: asyncio.Event = field(default_factory=asyncio.Event)  # maybe useless

    @property
    def id(self) -> int | None:
        return self._steam_offer.id if self._steam_offer._has_been_sent else None

    @property
    def state(self):
        return self._steam_offer.state

    @property
    def escrow(self):
        return self._steam_offer.escrow

    @property
    def message(self):
        return self._steam_offer.message

    @property
    def token(self):
        return self._steam_offer.token

    @property
    def expires(self):
        return self._steam_offer.expires

    @property
    def updated_at(self):
        return self._steam_offer.updated_at

    @property
    def created_at(self):
        return self._steam_offer.created_at

    @property
    def items_to_send(self):
        return self._steam_offer.items_to_send

    @property
    def items_to_receive(self):
        return self._steam_offer.items_to_receive

    @property
    def is_gift(self) -> bool:
        return self._steam_offer.is_gift()  # properly call it 'asking for a gift' :)

    @property
    def is_our_offer(self) -> bool:  # pragma: no cover
        return True  # "ManagerTradeOffer" wrap only our offers

    @property
    def is_active(self) -> bool:
        return self.state in (TradeOfferState.Active, TradeOfferState.ConfirmationNeed)

    @property
    def cancel_delay(self) -> timedelta | None:
        return self._cancel_delay if self._cancel_delay is not None else self.owner.offer_cancel_delay

    @cancel_delay.setter
    def cancel_delay(self, value: timedelta | None):
        self._cancel_delay = value

    def send(self) -> Coroutine[Any, Any, None]:
        """
        Send this prepared offer to partner.
        """
        return self.owner.send_offer(self)

    def _set_cancel_timeout(self):
        async def _cancel_timeout():
            await asyncio.sleep(self.cancel_delay.total_seconds())
            if self.is_active:
                await self.cancel()

        loop: asyncio.AbstractEventLoop = self.owner.loop  # type hinting won't work :(
        self._cancel_delay_timer = loop.create_task(_cancel_timeout())

    async def confirm(self):
        """Confirms the trade offer.
        This rarely needs to be called as the client handles most of these."""
        await self._steam_offer.confirm()
        self._cancel_delay_timer.cancel()

    async def cancel(self):
        try:
            await self._steam_offer.cancel()
        finally:
            self._cancel_delay_timer.cancel()

    # def check(self, pre=False) -> bool:
    #     """Check offer state and return `True` if state valid
    #     or trade is accepted otherwise return `False`."""
    #
    #     if pre:  # before update
    #         invalid_states = {
    #             steam.TradeOfferState.Invalid,
    #             steam.TradeOfferState.InvalidItems,
    #             steam.TradeOfferState.ConfirmationNeed,
    #             steam.TradeOfferState.CanceledBySecondaryFactor,
    #         }
    #     else:  # after
    #         invalid_states = {
    #             steam.TradeOfferState.Countered,
    #             steam.TradeOfferState.Declined,
    #             steam.TradeOfferState.Canceled,
    #         }
    #
    #     return self.state not in invalid_states

    @classmethod
    def _from_steam_trade_offer(cls, offer: TradeOffer, owner: _B) -> "ManagerTradeOffer":
        return cls(_steam_offer=offer, owner=owner, partner=offer.partner)

    def __hash__(self) -> int:
        return self.id

    def __eq__(self, other: TradeOfferAlias) -> bool:
        return self.id == other.id


from . import bot
