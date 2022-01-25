from datetime import timedelta
from time import time

import steam

BOT_USERNAME = "Bot username"
BOT_PASSWORD = "Bot password"
SHARED_SECRET = "Bot shared secret"
IDENTITY_SECRET = "Bot identity secret"
BOT_USER_NAME = "Bot-test"
BOT_ID = 76561198081339055


_ci = 0


def bot_trade_url():
    return f"https://steamcommunity.com/tradeoffer/new/?partner={steam.SteamID(BOT_ID + _ci).id}&token=BOT_URL_TOKEN"


BOTS_COUNT = 4


def bot_data():
    return {
        "username": BOT_USERNAME,
        "password": BOT_PASSWORD,
        "shared_secret": SHARED_SECRET,
        "identity_secret": IDENTITY_SECRET,
        "id": BOT_ID,
    }


USER_ID = 76561198081331111
USER_TOKEN = "USER_URL_TOKEN"
USER_TRADE_URL = f"https://steamcommunity.com/tradeoffer/new/?partner={steam.SteamID(USER_ID).id}&token={USER_TOKEN}"


def user_dict():
    return {
        "steamid": str(USER_ID),
        "personaname": "Persona USER",
        "primaryclanid": str(USER_ID),
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
        "timecreated": time() - 3600 * 24 * 12,
        "lastlogoff": time() - 3600 * 24 * 2,
        "last_logon": time() - 3600 * 12,
        "last_seen_online": time() - 3600 * 1.5,
    }


def client_user_dict():
    global _ci
    _ci += 1
    return {
        "steamid": str(BOT_ID + _ci),
        "personaname": "Persona" + str(_ci),
        "primaryclanid": str(BOT_ID + _ci),
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
        "timecreated": time() - 3600 * 24 * 12,
        "lastlogoff": time() - 3600 * 24 * 2,
        "last_logon": time() - 3600 * 12,
        "last_seen_online": time() - 3600 * 1.5,
    }


TRADE_MSG = "Trade message"
TRADE_URL = "https://steamcommunity.com/tradeoffer/new/?partner=2096455343&token=URL_TOKEN"
TRADE_ESCROW = timedelta(minutes=1)


_ti = 0


def trade_data():
    global _ti
    _ti += 1
    return {
        "tradeofferid": str(1234 + _ti),
        "tradeid": str(111 + _ti),  # only used for receipts (its not the useful one)
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
        "confirmation_method": 1,  # 2 is mobile 1 might be email? not a clue what other values are
    }


ITEMS_COUNT = 4
ITEM_CLASSID = "123"
ITEMS_GAME = steam.CSGO
DESCRIPTION_DATA = {
    "instanceid": None,
    "classid": ITEM_CLASSID,
    "market_name": "some item",
    "currency": 2,
    "name": "some item",
    "market_hash_name": "some item",
    "name_color": "445566",
    "background_color": "hex color :)",  # hex code
    "type": "rocket",
    "descriptions": {"desc_key": "desc_value"},
    "market_actions": [{"action_name": "action_value"}],
    "actions": [{"action_name": "action_value"}],
    "tags": [{"tag_name": "tag_value"}],
    "icon_url": "https://someurl.com",
    "icon_url_large": "https://someurl.com",
    "tradable": 1,  # 1 vs 0
    "marketable": 1,  # same as above
    "commodity": 1,  # might be a bool
    "fraudwarnings": ["don't know what is this", "nah"],
}

ASSET_DATA = {
    "assetid": None,
    "amount": 1,
    "appid": ITEMS_GAME.id,
    "contextid": str,
    "instanceid": None,
    "classid": ITEM_CLASSID,
    "missing": False,  # ?
}

_ii = 0


def inventory_data(count: int):
    global _ii
    data = {
        "assets": [{**ASSET_DATA, "instanceid": i, "assetid": i} for i in range(_ii + 1, 1 + count + _ii)],
        "descriptions": [{**DESCRIPTION_DATA, "instanceid": i} for i in range(_ii + 1, 1 + count + _ii)],
        "total_inventory_count": count,
        "success": 1,  # Result
        "rwgrsn": -2,  # p. much always -2
    }
    _ii += count
    return data
