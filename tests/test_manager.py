import asyncio

import pytest

from data import *
from steam_tradeoffer_manager import ManagerBot, TradeOfferManager
from steam_tradeoffer_manager.base.exceptions import ConstraintException


class TestManager:
    @staticmethod
    def get_bot(index: int) -> ManagerBot:
        return ManagerBot(**{
            "username": BOT_USERNAME + str(index),
            "password": BOT_PASSWORD,
            "shared_secret": SHARED_SECRET,
            "identity_secret": IDENTITY_SECRET,
            "id": BOT_ID + index
        })

    @pytest.fixture(scope="class")
    async def manager(self, event_loop):
        manager_instance = TradeOfferManager()
        manager_instance.loop = event_loop
        manager_instance.prefetch_games = (ITEMS_GAME,)

        yield manager_instance

        await manager_instance.shutdown()

    @pytest.mark.parametrize("index", [ii for ii in range(1, BOTS_COUNT + 1)])
    def test_add(self, manager, index):
        bot = self.get_bot(index)
        manager.add(bot)
        assert bot.manager == manager

    def test_len(self, manager):
        assert len(manager) == BOTS_COUNT

    def test_add_exception(self, manager):
        bot: ManagerBot = next(iter(manager))

        with pytest.raises(ConstraintException):
            manager.add(bot)

    def test_add_warning(self, manager):
        bot: ManagerBot = next(iter(manager))

        with pytest.warns(Warning):
            manager.add(bot, raise_=False)

    @pytest.mark.asyncio
    async def test_startup(self, manager):
        await manager.startup()

        bot: ManagerBot = next(iter(manager))
        assert bot.is_ready()

    @pytest.mark.asyncio
    async def test_offer_create(self, manager):
        bot: ManagerBot = next(iter(manager))
        item = bot.inventory.items[0]
        user = await bot.fetch_user(USER_ID)
        offer = manager.create_offer(
            user,
            USER_TOKEN,
            TRADE_MSG,
            [item],
        )
        await offer.send()
        await asyncio.sleep(.01)  # wait for dispatch to manager and add offer to trades

        assert len(manager.trades) == 1

    @pytest.mark.asyncio
    async def test_offer_create_from_url(self, manager):
        bot: ManagerBot = next(iter(manager))
        item = bot.inventory.items[0]
        offer = await manager.create_offer_from_url(
            TRADE_URL,
            TRADE_MSG,
            [item],
        )
        await offer.send()
        await asyncio.sleep(.01)  # wait for dispatch to manager and add offer to trades

        assert offer in manager.trades

    @pytest.mark.asyncio
    async def test_offers_create(self, manager):
        bot: ManagerBot = next(iter(manager))
        user = await bot.fetch_user(USER_ID)

        items = [bot.inventory.items for bot in manager]
        offer_items = []
        for bot_items in items:
            offer_items.append(bot_items[0])

        offers = manager.create_offers(
            user,
            USER_TOKEN,
            TRADE_MSG,
            offer_items,
        )
        assert len(offers) == len(manager)

    @pytest.mark.asyncio
    async def test_offers_create_from_url(self, manager):
        items = [bot.inventory.items for bot in manager]
        offer_items = []
        for bot_items in items:
            offer_items.append(bot_items[0])

        offers = await manager.create_offers_from_url(
            TRADE_URL,
            TRADE_MSG,
            offer_items,
        )
        assert len(offers) == len(manager)

    def test_remove(self, manager):
        bot: ManagerBot = next(iter(manager))
        manager.remove(bot)

        assert not bot.manager
