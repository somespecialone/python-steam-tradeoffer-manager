import pytest

from const_data import *


class TestBot:
    @pytest.mark.asyncio
    async def test_start(self, bot):
        await bot.start()
        assert bot.is_ready()

    # TODO: domain, prefetch games etc.
    def test_domain(self, bot):
        ...

    @pytest.mark.asyncio
    async def test_trade_url(self, bot):
        await bot.generate_trade_url()
        assert bot.trade_url == BOT_TRADE_URL

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
