import pytest

from steam import TradeOfferState, ClientException
from steam_tradeoffer_manager import ManagerTradeOffer, ManagerBot
from steam_tradeoffer_manager.utils import parse_trade_url

from const_data import *


# TODO: explicit offer methods test cases
# @pytest.mark.asyncio
# async def test_offer_properties(trade: ManagerTradeOffer):
#     trade._steam_offer.escrow = TRADE_ESCROW
#     assert trade.escrow == TRADE_ESCROW
#
#     _, trade._steam_offer.token = parse_trade_url(TRADE_URL)
#     assert trade.token == parse_trade_url(TRADE_URL)[1]


@pytest.mark.asyncio
async def test_offer_send_close(trade: ManagerTradeOffer, bot):
    await trade.send()

    assert trade.id

    await trade.cancel()

    with pytest.raises(ClientException):
        await trade.cancel()
