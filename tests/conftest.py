import asyncio
import platform

import pytest

from steam_tradeoffer_manager import ManagerBot, ManagerTradeOffer

from mocks import *
from const_data import *


@pytest.fixture
def bot_data():
    return {
        "username": BOT_USERNAME,
        "password": BOT_PASSWORD,
        "shared_secret": SHARED_SECRET,
        "identity_secret": IDENTITY_SECRET,
    }


@pytest.fixture(scope="session")
def event_loop():
    """Prevent warning on Windows"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def bot(event_loop):
    bot_instance = ManagerBot(**{
        "username": BOT_USERNAME,
        "password": BOT_PASSWORD,
        "shared_secret": SHARED_SECRET,
        "identity_secret": IDENTITY_SECRET,
    })
    bot_instance.loop = event_loop
    await bot_instance.start()

    yield bot_instance

    bot_instance.__del__()


@pytest.fixture
async def trade(bot, bot_data):
    trade_instance: ManagerTradeOffer = await bot.create_offer_from_trade_url(TRADE_URL, message=TRADE_MSG)
    trade_instance.cancel_delay = timedelta(seconds=0)  # instant cancellation
    return trade_instance
