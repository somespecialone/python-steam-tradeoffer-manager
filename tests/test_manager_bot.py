import pytest

from const_data import *


@pytest.mark.asyncio
async def test_bot_start(bot):
    assert bot.is_ready()


@pytest.mark.asyncio
async def test_bot_properties(bot):
    # TODO: domain, prefetch games etc.
    ...


@pytest.mark.asyncio
async def test_bot_misc(bot):
    await bot.generate_trade_url()
    assert bot.trade_url == BOT_TRADE_URL


@pytest.mark.asyncio
async def test_bot_close(bot):
    await bot.close()
    assert bot.is_closed() and not bot.is_ready()
