import urllib.parse
from functools import wraps
from typing import Protocol, Sequence

import steam.state

from .base import ReadyRequired

__all__ = ('ready_required', "parse_trade_url", "join_multiple_in_string")


class _HasIsReadyProtocol(Protocol):
    def is_ready(self) -> bool: ...


def ready_required(func):
    @wraps(func)  # FIXME: why this won't work?
    def wrapper(self: _HasIsReadyProtocol, *args, **kwargs):
        if self.is_ready():
            return func(self, *args, **kwargs)
        else:
            raise ReadyRequired("Client is not ready or bot is closed/stopped!")
    return wrapper


# def ready_required(exc: Exception):
#     def inner(func):
#         @wraps(func)
#         def wrapper(self: _HasIsReadyProtocol, *args, **kwargs):
#             if self.is_ready():
#                 return func(self, *args, **kwargs)
#             else:
#                 raise exc("Client is not ready or bot is closed/stopped!")
#         return wrapper
#
#     return inner

def parse_trade_url(trade_url: str) -> tuple[int, str]:
    qs = urllib.parse.parse_qs(urllib.parse.urlparse(trade_url).query)
    return int(qs['partner'][0]), qs['token'][0]


def join_multiple_in_string(fs: Sequence) -> str:
    # https://stackoverflow.com/a/59721058
    return " , ".join(["{}"] * len(fs)).format(*fs)


class _HasConnectionState(Protocol):
    _connection: steam.state.ConnectionState


def copy_user(bot: _HasConnectionState, user: steam.User) -> steam.User:
    """Deepcopy `steam.User` and cache it in client"""
    user_data = {
        "steamid": user.id64,
        "personaname": user.name,
        "profileurl": user.community_url,
        "realname": user.real_name,
        "communityvisibilitystate": user.privacy_state.value if user.privacy_state else 0,
        "profilestate": user._setup_profile,
        "commentpermission": user._is_commentable,
        "personastate": user.state.value if user.state else 0,
        "personastateflags": user.flags.value if user.flags else 0,
        "avatar": "",
        "avatarmedium": "",
        "avatarfull": user.avatar_url,
        "avatarhash": "",
        "loccountrycode": user.country,
        "locstatecode": 0,
        "loccityid": 0,
    }
    if user.primary_clan:
        user_data |= {"primaryclanid": user.primary_clan.id64}
    if user.created_at:
        user_data |= {"timecreated": user.created_at.timestamp()}
    if user.last_logoff:
        user_data |= {"lastlogoff": user.last_logoff.timestamp()}
    if user.last_logon:
        user_data |= {"last_logon": user.last_logon.timestamp()}
    if user.last_seen_online:
        user_data |= {"last_seen_online": user.last_seen_online.timestamp()}
    if user.game:
        user_data |= {"gameextrainfo": user.game.name, "gameid": user.game.id}

    new_user = steam.User(state=bot._connection, data=user_data)
    bot._connection._users[user.id64] = new_user

    return new_user
