import asyncio
import platform

import pytest

from mocks import *
from data import *
from steam_tradeoffer_manager import ManagerBot, TradeOfferManager


@pytest.fixture(scope="session")
def event_loop():
    """Prevent warning on Windows"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    # loop.close() # don't know why but this throws many warnings about destroying pending tasks


@pytest.fixture(scope="class")
async def bot(event_loop):
    bot_instance = ManagerBot(**bot_data())
    bot_instance.loop = event_loop

    yield bot_instance

    if not bot_instance.is_closed():
        await bot_instance.close()

    bot_instance.__del__()
