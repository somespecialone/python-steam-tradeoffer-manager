import asyncio

import pytest
import steam
from pytest_mock import MockerFixture

from data import *
from steam_tradeoffer_manager import ManagerTradeOffer


class TestBot:
    NEW_ITEMS_COUNT = ITEMS_COUNT + 1

    @pytest.mark.asyncio
    async def test_start(self, bot):
        await bot.start()
        assert bot.is_ready()

    @pytest.mark.asyncio
    async def test_trade_url(self, bot):
        await bot.generate_trade_url()
        assert bot.trade_url == bot_trade_url()

    @pytest.mark.asyncio
    async def test_inventory(self, bot):
        await bot.inventory.fetch_game_inventory(ITEMS_GAME)
        assert bot.inventory.get(ITEMS_GAME)

    @pytest.mark.asyncio
    async def test_inventory_update(self, bot, mocker: MockerFixture):
        async def update(self_bi: steam.trade.BaseInventory):
            self_bi._update(inventory_data(self.NEW_ITEMS_COUNT))

        mocker.patch.object(steam.trade.BaseInventory, "update", update)

        await bot.inventory.update_all()
        assert len(bot.inventory) == self.NEW_ITEMS_COUNT

    @pytest.mark.asyncio
    async def test_all_inventory(self, bot):
        inv = bot.inventory.get(ITEMS_GAME)
        assert bot.inventory.game_inventories == [inv]

    @pytest.mark.asyncio
    async def test_items(self, bot):
        assert len(bot.inventory.items) == self.NEW_ITEMS_COUNT

    @pytest.mark.asyncio
    async def test_close_tradeoffer(self, bot):
        offer: ManagerTradeOffer = await bot.create_offer_from_trade_url(TRADE_URL, message=TRADE_MSG)
        offer.cancel_delay = timedelta(minutes=1)
        await offer.send()
        await offer.cancel()
        await asyncio.sleep(0.01)  # wait for dispatch and cancel timer

        assert offer._cancel_delay_timer.cancelled()

    @pytest.mark.asyncio
    async def test_bot_close(self, bot):
        await bot.close()
        assert bot.is_closed() and not bot.is_ready()

    @pytest.mark.asyncio
    async def test_bot_restart(self, bot):
        bot.randomizer = lambda: 0.5  # delay before restart in seconds
        await bot.start()

        await bot.wait_for("logout", timeout=1)
        assert not bot.is_closed()

        await bot.wait_for("ready", timeout=1)
        assert bot.is_ready()


class TestBotDeletion:
    @pytest.mark.asyncio
    async def test_del(self, bot):
        await bot.start()
        with pytest.warns(ResourceWarning):
            bot.__del__()


class TestBotWhitelist:
    @pytest.mark.asyncio
    async def test_whitelist(self, bot):
        await bot.start()
        bot.whitelist = (USER_ID,)
        trade = steam.TradeOffer()
        trade.partner = steam.User(bot._connection, {**user_dict(), "steamid": USER_ID})
        trade._has_been_sent = True
        data = [
            {
                **ASSET_DATA,
                **DESCRIPTION_DATA,
                "assetid": 123,
                "instanceid": 1234,
            }
        ]
        trade._update({**trade_data(), "items_to_receive": data, "is_our_offer": False})

        bot.dispatch("trade_receive", trade)
        await asyncio.sleep(1)

        assert bot.inventory.get_game_inventory(ITEMS_GAME)
