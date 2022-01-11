import asyncio
import platform
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

import steam
from steam_tradeoffer_manager import ManagerBot

USER_DICT = {
    "steamid": "76561198081339055",
    "personaname": "str",
    "primaryclanid": "76561198081339055",
    "profileurl": "str",
    "realname": "str",
    "communityvisibilitystate": 123,
    "profilestate": 123,
    "commentpermission": 123,
    "personastate": 123,
    "personastateflags": 123,
    "avatar": "str",
    "avatarmedium": "str",
    "avatarfull": "str",
    "avatarhash": "str",
    "loccountrycode": "2",
    "locstatecode": 123,
    "loccityid": 123,
    "gameid": "730",  # game app id
    "gameextrainfo": "str",  # game name
    "timecreated": 123,
    "lastlogoff": 123,
    "last_logon": 123,
    "last_seen_online": 123,
}


@pytest.fixture
def unmocked_user_instance():
    return steam.User(None, USER_DICT)


@pytest.fixture
def user_instance(unmocked_user_instance, mocker: MockerFixture):
    """Mock required methods of `steam.User`"""
    user = unmocked_user_instance
    # mocker.patch.object(user, "send")

    return user


@pytest.fixture
def unmocked_bot_instance():
    return ManagerBot(
        "Bot username",
        "Bot password",
        "Bot shared_secret",
        "Bot identity_secret"
    )


@pytest.fixture
def bot_instance(unmocked_bot_instance, user_instance, mocker: MockerFixture):
    """Mock required methods of `steam.Client`"""
    bot = unmocked_bot_instance
    mocker.patch.object(bot, "is_ready", lambda: True)
    mocker.patch.object(bot, "fetch_user", AsyncMock(return_value=user_instance))

    return bot


@pytest.fixture(autouse=True)
def patch_event_loop():
    """Prevent warning on Windows"""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
