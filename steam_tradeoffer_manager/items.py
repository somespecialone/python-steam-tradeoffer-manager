from typing import TypeVar, Iterator, Generic, TypeAlias
from collections.abc import MutableMapping
from weakref import WeakValueDictionary

from .item import BotItem

__all__ = ("ManagerItems",)

_B = TypeVar("_B", bound="bot.ManagerBot")
_M = TypeVar("_M", bound="manager.TradeOfferManager")
_D = TypeVar("_D")
AssetId: TypeAlias = "int"
ItemAlias: TypeAlias = "int | BotItem"


# extremely rarely asset id can be not unique
class ManagerItems(MutableMapping[AssetId, BotItem[_B]], Generic[_M, _B]):
    """Items storage for TradeOfferManager.
    Contain all items from `ManagerBot` bounded to `owner` manager"""

    def __init__(self, owner: _M):
        self.owner = owner
        self._storage: WeakValueDictionary[AssetId, BotItem] = WeakValueDictionary()

    def add(self, item: BotItem):
        self[item.asset_id] = item

    def get(self, k: AssetId, _default: _D = None) -> BotItem | _D:
        return self._storage.get(k, _default)

    def pop(self, id: AssetId) -> BotItem:
        return self._storage.pop(id)

    def __setitem__(self, k: AssetId, v: BotItem) -> None:
        if k == v.asset_id:
            raise ValueError("Key and asset id must be the same")
        self._storage[k] = v

    def __delitem__(self, v: AssetId) -> None:
        del self._storage[v]

    def __getitem__(self, k: AssetId) -> BotItem:
        return self._storage[k]

    def __len__(self) -> int:
        return len(self._storage)

    def __iter__(self) -> Iterator[BotItem]:
        return iter(self._storage.values())

    def __contains__(self, item: ItemAlias) -> bool:
        return item in self._storage if isinstance(item, AssetId) else item.asset_id in self._storage


from . import manager, bot
