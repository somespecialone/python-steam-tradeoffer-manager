import asyncio
import platform

import pytest

from steam_tradeoffer_manager import ManagerBot

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.mark.asyncio
async def test_loop():
    await asyncio.sleep(1)
