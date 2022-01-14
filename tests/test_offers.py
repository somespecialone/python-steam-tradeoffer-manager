import asyncio

import pytest
from steam import ClientException

from data import *
from steam_tradeoffer_manager import ManagerTradeOffer
from steam_tradeoffer_manager.utils import parse_trade_url


class TestOffer:
    @pytest.fixture(scope="class")
    async def trade(self, bot):
        await bot.start()
        trade_instance: ManagerTradeOffer = await bot.create_offer_from_trade_url(TRADE_URL, message=TRADE_MSG)
        trade_instance.cancel_delay = timedelta(seconds=0)  # instant cancellation
        return trade_instance

    @pytest.mark.asyncio
    async def test_send(self, trade: ManagerTradeOffer):
        await trade.send()
        assert trade.id

    @pytest.mark.asyncio
    async def test_cancel(self, trade: ManagerTradeOffer):
        await asyncio.sleep(0.01)  # waiting for auto cancel (run event loop iteration)
        with pytest.raises(ClientException):
            await trade.cancel()

    def test_escrow(self, trade: ManagerTradeOffer):
        assert trade.escrow

    def test_token(self, trade: ManagerTradeOffer):
        assert trade.token == parse_trade_url(TRADE_URL)[1]

    def test_message(self, trade: ManagerTradeOffer):
        assert trade.message == TRADE_MSG

    def test_expires(self, trade: ManagerTradeOffer):
        assert trade.expires

    def test_updated_at(self, trade: ManagerTradeOffer):
        assert trade.updated_at

    def test_created_at(self, trade: ManagerTradeOffer):
        assert trade.created_at

    def test_items(self, trade: ManagerTradeOffer):
        assert trade.items_to_send == trade.items_to_receive == []

    def test_is_gift(self, trade: ManagerTradeOffer):
        assert not trade.is_gift

    def test_hash(self, trade: ManagerTradeOffer):
        assert hash(trade) == trade.id

    def test_eq(self, trade: ManagerTradeOffer):
        assert trade == trade._steam_offer
