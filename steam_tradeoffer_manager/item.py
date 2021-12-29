from typing import TypeVar, Generic

from steam import Item, utils

__all__ = ("BotItem",)

_O = TypeVar("_O", bound="bot.ManagerBot")


class BotItem(Item, Generic[_O]):
    """Almost `steam.Item` except one thing - `owner is `ManagerBot``"""
    owner: _O

    def __init__(self, item: Item, owner: _O):
        utils.update_class(item, self)
        self.owner = owner

    def __hash__(self) -> int:
        return hash((self.asset_id, self._app_id))


from . import bot
