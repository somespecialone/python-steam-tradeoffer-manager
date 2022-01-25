from typing import TypeVar, Iterator, Generic, TypeAlias
from collections.abc import MutableMapping
from weakref import WeakValueDictionary

from steam import TradeOffer

from .offer import ManagerTradeOffer


__all__ = ("ManagerBotTrades", "ManagerTrades")

_B = TypeVar("_B", bound="bot.ManagerBot")
_M = TypeVar("_M", bound="manager.TradeOfferManager")
_D = TypeVar("_D")
TradeOfferId: TypeAlias = "int"
ItemAlias: TypeAlias = "int | ManagerTradeOffer | TradeOffer"


class ManagerBotTrades(MutableMapping[TradeOfferId, ManagerTradeOffer[_B]], Generic[_B]):
    """
    ManagerTradeOffer's storage for ManagerBot.
    """

    __slots__ = ("owner", "_storage")

    def __init__(self, owner: _B):
        self.owner = owner
        self._storage: dict[TradeOfferId, ManagerTradeOffer] = {}

    def add(self, offer: ManagerTradeOffer):
        if not offer.id:
            raise ValueError("Only sent offers can be stored")

        if offer.id in self:
            import warnings

            warnings.warn(f"Trade offer {offer.id} already in storage!")

        self[offer.id] = offer

    def clear(self) -> None:
        """Remove all closed offers from storage"""
        for offer in self:
            if not offer.is_active:
                del self[offer.id]

    def get(self, k: TradeOfferId, _default: _D = None) -> ManagerTradeOffer | _D:
        return self._storage.get(k, _default)

    def pop(self, id: TradeOfferId) -> ManagerTradeOffer:
        offer = self[id]
        del self[id]
        return offer

    def __setitem__(self, k: TradeOfferId, v: ManagerTradeOffer) -> None:
        if not v.id:
            raise ValueError("Only sent offers can be stored")
        if k != v.id:
            raise ValueError("Key and offer id must be the same")
        self._storage[k] = v

    def __delitem__(self, v: TradeOfferId) -> None:
        if self[v].is_active:
            raise TypeError("You can't delete active offer!")
        del self._storage[v]

    def __getitem__(self, k: TradeOfferId) -> ManagerTradeOffer:
        return self._storage[k]

    def __len__(self) -> int:
        return len(self._storage)

    def __iter__(self) -> Iterator[ManagerTradeOffer]:
        return iter(self._storage.values())

    def __contains__(self, item: ItemAlias) -> bool:
        return item in self._storage if isinstance(item, int) else item.id in self._storage


class ManagerTrades(ManagerBotTrades[_M]):
    """ManagerTradeOffer's storage for TradeOfferManager.
    Contain all trade offers from `ManagerBot` bounded to `owner` manager"""

    def __init__(self, owner: _M):
        super().__init__(owner)
        self._storage: WeakValueDictionary[TradeOfferId, ManagerTradeOffer] = WeakValueDictionary()


from . import bot, manager
