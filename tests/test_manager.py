import pytest

from const_data import *
from steam_tradeoffer_manager import ManagerBot, TradeOfferManager


class TestManager:
    i = 0

    def get_bot(self):
        self.i += 1
        return ManagerBot(**{
            "username": BOT_USERNAME + str(self.i),
            "password": BOT_PASSWORD,
            "shared_secret": SHARED_SECRET,
            "identity_secret": IDENTITY_SECRET,
            "id": BOT_ID + self.i
        })

    @pytest.fixture(scope="class")
    async def manager(self, event_loop):
        manager_instance = TradeOfferManager()
        manager_instance.loop = event_loop

        yield manager_instance

        await manager_instance.shutdown()

    def test_add(self, manager):
        bot = self.get_bot()
        manager.add(bot)
        assert bot.manager == manager

    # TODO: offers creation tests, add items to bot

    def test_remove(self, manager):
        bot: ManagerBot = next(iter(manager))
        manager.remove(bot)

        assert not bot.manager
