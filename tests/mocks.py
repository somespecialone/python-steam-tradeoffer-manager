import asyncio
from unittest.mock import AsyncMock

import pytest
import steam.trade
from pytest_mock import MockerFixture

from data import *

__all__ = ("mock_user", "mock_client", "mock_trade", "mock_client_user", "mock_inventory")


async def send(
        self: steam.User,
        content=None,
        *,
        trade: steam.TradeOffer | None = None,
        image: steam.Image | None = None,
):
    trade._update_from_send(self._state, trade_data(), self, active=True)
    trade.state = steam.TradeOfferState.Active

    trade._update(trade_data())
    trade._has_been_sent = True

    self._state.dispatch("trade_send", trade)
    return TRADE_MSG


@pytest.fixture(scope="session", autouse=True)
def mock_user(session_mocker: MockerFixture):
    session_mocker.patch.object(steam.User, "send", send)


class WsMock:
    def __init__(self, state):
        self._connection = state

    async def change_presence(self, *args, **kwargs): pass

    async def handle_close(self): pass


async def login(self: steam.Client, username: str, password: str, *, shared_secret: str | None = None):
    self.username = self.http.username = username
    self.password = self.http.password = password
    self.shared_secret = self.http.shared_secret = shared_secret

    self._closed = False

    self.http.logged_in = True
    self.http.user = steam.ClientUser(state=self._connection, data=client_user_dict())
    self.http.user.name = BOT_USER_NAME
    self.dispatch("login")


async def connect(self: steam.Client):
    self.ws = WsMock(self._connection)
    await self._handle_ready()
    while not self.is_closed():
        await asyncio.sleep(1)


async def fetch_user(self: steam.Client, id: steam.utils.Intable):
    id64 = steam.utils.make_id64(id=id, type=steam.Type.Individual)
    return steam.User(self._connection, {**user_dict(), "steamid": id64})


async def close(self: steam.Client) -> None:
    if self.is_closed():
        return

    self._closed = True

    self.http.logged_in = False
    self.http.user = None
    self.dispatch("logout")

    self._ready.clear()


@pytest.fixture(scope="session", autouse=True)
def mock_client(session_mocker: MockerFixture):
    """Mock required methods of `steam.Client`"""
    session_mocker.patch.object(steam.Client, "login", login)
    session_mocker.patch.object(steam.Client, "connect", connect)
    session_mocker.patch.object(steam.Client, "close", close)
    session_mocker.patch.object(steam.Client, "trade_url", AsyncMock(return_value=bot_trade_url()))
    session_mocker.patch.object(steam.Client, "fetch_user", fetch_user)


async def inventory(self: steam.ClientUser, game: steam.Game):
    return steam.Inventory(self._state, inventory_data(ITEMS_COUNT), self, game)


@pytest.fixture(scope="session", autouse=True)
def mock_client_user(session_mocker: MockerFixture):
    session_mocker.patch.object(steam.ClientUser, "inventory", inventory)


async def update(self: steam.trade.BaseInventory):
    self._update(inventory_data(ITEMS_COUNT))


@pytest.fixture(scope="session", autouse=True)
def mock_inventory(session_mocker: MockerFixture):
    session_mocker.patch.object(steam.trade.BaseInventory, "update", update)


async def cancel(self: steam.TradeOffer):
    if self.state == steam.TradeOfferState.Canceled:
        raise steam.ClientException("This trade has already been cancelled")
    self._check_active()

    self.state = steam.TradeOfferState.Canceled


async def accept(self: steam.TradeOffer):
    self.state = steam.TradeOfferState.Accepted


@pytest.fixture(scope="session", autouse=True)
def mock_trade(session_mocker: MockerFixture):
    session_mocker.patch.object(steam.TradeOffer, "cancel", cancel)
    session_mocker.patch.object(steam.TradeOffer, "accept", accept)
