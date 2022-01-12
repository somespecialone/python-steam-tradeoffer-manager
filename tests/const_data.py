from datetime import timedelta
from time import time

BOT_USERNAME = "Bot username"
BOT_PASSWORD = "Bot password"
SHARED_SECRET = "Bot shared secret"
IDENTITY_SECRET = "Bot identity secret"
BOT_TRADE_URL = "https://steamcommunity.com/tradeoffer/new/?partner=2096455343&token=BOT_URL_TOKEN"

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

CLIENT_USER_DICT = {
    "steamid": "76565190081339055",
    "personaname": "str",
    "primaryclanid": "76565190081339055",
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

TRADE_MSG = "Trade message"
TRADE_URL = "https://steamcommunity.com/tradeoffer/new/?partner=2096455343&token=URL_TOKEN"
TRADE_ESCROW = timedelta(minutes=1)

TRADE_DATA = {
    "tradeofferid": "1234",
    "tradeid": "111",  # only used for receipts (its not the useful one)
    "accountid_other": 1234567,
    "message": TRADE_MSG,
    "trade_offer_state": 2,  # TradeOfferState
    "expiration_time": time() + 3600,  # unix timestamps
    "time_created": time() - 2,
    "time_updated": time(),
    "escrow_end_date": time() + 500,
    "items_to_give": [],
    "items_to_receive": [],
    "is_our_offer": True,
    "from_real_time_trade": False,
    "confirmation_method": 1  # 2 is mobile 1 might be email? not a clue what other values are
}
