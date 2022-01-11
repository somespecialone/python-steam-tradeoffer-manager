import urllib.parse
from functools import wraps
from typing import Protocol, Sequence

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
