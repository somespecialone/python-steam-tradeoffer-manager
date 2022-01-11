import asyncio
import platform

import pytest

from steam_tradeoffer_manager import ManagerBot


@pytest.mark.asyncio
async def test_loop():
    await asyncio.sleep(1)
