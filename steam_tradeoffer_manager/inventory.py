from typing import Iterator, TypeVar, Generic, TypeAlias, overload
from collections.abc import MutableMapping
from weakref import WeakValueDictionary

from steam.trade import Game, StatefulGame, BaseInventory

from .item import BotItem

__all__ = ("GamesInventory",)

_B = TypeVar("_B", bound='bot.ManagerBot')
_D = TypeVar("_D")
SteamGame: TypeAlias = "Game | StatefulGame"
BotInventory: TypeAlias = "BaseInventory[BotItem[_B]]"
AssetId: TypeAlias = "int"
AnyType: TypeAlias = "Game | StatefulGame | int"


class GamesInventory(MutableMapping[AssetId, BotItem[_B]], Generic[_B]):
    """Container class created to store fetched inventories"""

    __slots__ = ('_storage', 'owner', "_inventory_storage")

    def __init__(self, owner: _B):
        self._inventory_storage: dict[int | str, BotInventory] = {}  # default inventories with refs to items
        self._storage: WeakValueDictionary[AssetId, BotItem[_B]] = WeakValueDictionary()  # weak refs to items
        self.owner = owner

    async def update_all(self) -> None:
        """Update all saved inventories"""
        for inv in self._inventory_storage.values():
            await inv.update()
            inv.items = tuple(map(lambda i: BotItem(i, self.owner), inv.items))
            self._storage.update({bot_item.asset_id: bot_item for bot_item in inv.items})

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
        return list(iter(self._inventory_storage.values()))

    @overload
    def get(self, game: SteamGame, default: _D = None) -> BotInventory | _D:
        """Get cached bot inventory"""

    def get(self, asset_id: AssetId, default: _D = None) -> BotItem[_B] | _D:
        """Get cached bot item"""
        return self._inventory_storage.get(asset_id.name or asset_id.id, default) if isinstance(asset_id, Game)\
            else self._storage.get(asset_id, default)

    async def fetch_game_inventory(self, game: SteamGame) -> BotInventory:
        """Fetch inventory from steam servers and cache it"""
        inv = await self.owner.user.inventory(game)  # again type hinting
        inv.items = tuple(map(lambda i: BotItem(i, self.owner), inv.items))
        self._inventory_storage[game.name or game.id] = inv
        self._storage.update({bot_item.asset_id: bot_item for bot_item in inv.items})

        self.owner.dispatch_to_manager("inventory_update", inv)

        return inv

    @overload
    def pop(self, game: SteamGame) -> BotInventory: ...

    def pop(self, asset_id: AssetId) -> BotItem[_B]:
        return self._inventory_storage.pop(asset_id.name or asset_id.id) if isinstance(asset_id, Game) \
            else self._storage.pop(asset_id)

    # mapping methods

    def __iter__(self) -> Iterator[BotItem[_B]]:
        return iter(self._storage.values())

    def __len__(self) -> int:
        return len(self._storage)

    def __getitem__(self, k: AnyType) -> BotItem[_B]:
        return self._inventory_storage[k.name or k.id] if isinstance(k, Game) else self._storage[k]

    def __delitem__(self, v: AssetId) -> None:
        del self._storage[v]

    def __setitem__(self, k: AssetId, v: BotItem[_B]) -> None:
        self._storage[k] = v

    def __contains__(self, k: AnyType) -> bool:
        return k.name or k.id in self._inventory_storage if isinstance(k, Game) else k in self._storage


from . import bot
