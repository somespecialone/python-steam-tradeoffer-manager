from typing import Iterator, TypeVar, Generic, TypeAlias
from collections.abc import MutableMapping
from weakref import WeakValueDictionary

from steam.trade import Game, StatefulGame, BaseInventory

from .item import BotItem

__all__ = ("GamesInventory",)

_B = TypeVar("_B", bound="bot.ManagerBot")
_D = TypeVar("_D")
SteamGame: TypeAlias = "Game | StatefulGame"
BotInventory: TypeAlias = "BaseInventory[BotItem[_B]]"
AssetId: TypeAlias = "int"


class GamesInventory(MutableMapping[AssetId, BotItem[_B]], Generic[_B]):
    """Container class created to store fetched inventories"""

    __slots__ = ("_items_storage", "owner", "_inventories_storage")

    def __init__(self, owner: _B):
        self._inventories_storage: dict[int, BotInventory] = {}  # default inventories with refs to items
        self._items_storage: WeakValueDictionary[AssetId, BotItem[_B]] = WeakValueDictionary()  # weak refs to items
        self.owner = owner

    async def update_all(self) -> None:
        """Update all saved inventories"""
        for inv in self._inventories_storage.values():
            await inv.update()
            inv.items = tuple(map(lambda i: BotItem(i, self.owner), inv.items))
            self._items_storage.update({bot_item.asset_id: bot_item for bot_item in inv.items})

            self.owner.dispatch_to_manager("inventory_update", inv)

    @property
    def items(self) -> list[BotItem[_B]]:
        """
        Get all items contains in inventories.
        :return: list[`BotItems`]
        """
        return list(iter(self))

    @property
    def game_inventories(self) -> list[BotInventory]:
        """
        Get all game inventories of this bot.
        :return: list[`BotInventory`]
        """
        return list(iter(self._inventories_storage.values()))

    def get(self, asset_id: AssetId, default: _D = None) -> BotItem[_B] | _D:
        """Get cached bot item."""
        return self._items_storage.get(asset_id, default)

    def get_game_inventory(self, game: SteamGame, default: _D = None) -> BotInventory | _D:
        """Get inventory for given game."""
        return self._inventories_storage.get(game.id, default)

    async def fetch_game_inventory(self, game: SteamGame) -> BotInventory:
        """Fetch inventory from steam servers and cache it."""
        inv: BaseInventory = await self.owner.user.inventory(game)  # again type hinting :(
        inv.items = tuple(map(lambda i: BotItem(i, self.owner), inv.items))
        self._inventories_storage[game.id] = inv
        self._items_storage.update({bot_item.asset_id: bot_item for bot_item in inv.items})

        self.owner.dispatch_to_manager("inventory_update", inv)

        return inv

    # mapping methods only for items

    def __iter__(self) -> Iterator[BotItem[_B]]:
        return iter(self._items_storage.values())

    def __len__(self) -> int:
        return len(self._items_storage)

    def __getitem__(self, k: AssetId) -> BotItem[_B]:
        return self._items_storage[k]

    def __delitem__(self, v: AssetId) -> None:
        del self._items_storage[v]

    def __setitem__(self, k: AssetId, v: BotItem[_B]) -> None:
        self._items_storage[k] = v

    def __contains__(self, k: AssetId) -> bool:
        return k in self._items_storage


from . import bot
