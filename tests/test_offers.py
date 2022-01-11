import pytest

from steam_tradeoffer_manager import ManagerTradeOffer

MSG = "Trade"
TRADE_URL = "https://steamcommunity.com/tradeoffer/new/?partner=76561198081339055&token=URL_TOKEN"


# def test_offer_create(bot_instance, user_instance):
#     MSG = "Trade"
#     trade: ManagerTradeOffer = bot_instance.create_offer(user_instance, message=MSG)
#     assert trade.message == MSG


@pytest.mark.asyncio
async def test_offer_create_trade_url(bot_instance):
    trade: ManagerTradeOffer = await bot_instance.create_offer_from_trade_url(TRADE_URL, message=MSG)
    assert trade.message == MSG
