import asyncio

import pytest
import steam
from pytest_mock import MockerFixture

from steam_tradeoffer_manager import ManagerBotState, ManagerBot

from data import *


class TestBotExceptions:
    @pytest.fixture
    async def bot(self, event_loop):
        bot_instance = ManagerBot(
            **{
                "username": BOT_USERNAME,
                "password": BOT_PASSWORD,
                "shared_secret": SHARED_SECRET,
                "identity_secret": IDENTITY_SECRET,
            }
        )
        bot_instance.loop = event_loop

        yield bot_instance

        if not bot_instance.is_closed():
            await bot_instance.close()
        bot_instance.__del__()

    @pytest.mark.asyncio
    async def test_timeout(self, bot, mocker: MockerFixture):
        async def connect(self: steam.Client):
            await asyncio.sleep(0.2)

        mocker.patch.object(steam.Client, "connect", connect)
        await bot.start(timeout=0.1)
        assert not bot.is_ready()

        await bot.close()

    @pytest.mark.asyncio
    async def test_login(self, bot, mocker: MockerFixture):
        error = steam.LoginError("L")

        async def login(self, *args, **kwargs):
            raise error

        mocker.patch.object(steam.Client, "login", login)

        await bot.start(timeout=0.1)

        assert bot.state == ManagerBotState.UnknownError
        assert error in bot.errors
        await bot.close()

    @pytest.mark.asyncio
    async def test_credentials(self, bot, mocker: MockerFixture):
        error = steam.InvalidCredentials("I")

        async def login(self, *args, **kwargs):
            raise error

        mocker.patch.object(steam.Client, "login", login)

        await bot.start(timeout=0.1)

        assert bot.state == ManagerBotState.InvalidCredentials
        assert error in bot.errors
        await bot.close()
