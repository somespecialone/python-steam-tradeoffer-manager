"""
Patch `steam.util.call_once` decorator func for handling many clients.
Patch `steam.http.get_api_key` to pass custom domain.
"""

import asyncio
import functools
import logging
import re

from steam import state, http, models

_log = logging.getLogger(__name__)


# Patched call_once for many clients
def call_once_patched(func):
    called: set[int] = set()

    @functools.wraps(func)
    async def inner(self: state.ConnectionState | state.TradesList, *args, **kwargs) -> None:
        nonlocal called

        id_ = self.client.user.id64 if isinstance(self, state.ConnectionState) else self._state.client.user.id64
        if id_ in called:  # call becomes a noop
            return await asyncio.sleep(0)

        called.add(id_)
        try:
            await func(self, *args, **kwargs)
        finally:
            called.remove(id_)

    return inner


@call_once_patched
async def poll_trades_patched(self: state.ConnectionState) -> None:
    await self.fill_trades()

    while self._trades_to_watch:
        await asyncio.sleep(5)
        await self.fill_trades()


state.ConnectionState.poll_trades = poll_trades_patched


async def get_api_key_patched(self: http.HTTPClient) -> str | None:
    resp = await self.get(models.URL.COMMUNITY / "dev/apikey")
    if (
            "<h2>Access Denied</h2>" in resp
            or "You must have a validated email address to create a Steam Web API key" in resp
    ):
        return

    key_re = re.compile(r"<p>Key: ([0-9A-F]+)</p>")
    match = key_re.findall(resp)
    if match:
        return match[0]

    payload = {
        "domain": getattr(self._client, "domain", "steam.py"),  # making sure patch wouldn't break something
        "agreeToTerms": "agreed",
        "sessionid": self.session_id,
        "Submit": "Register",
    }
    resp = await self.post(models.URL.COMMUNITY / "dev/registerkey", data=payload)
    return key_re.findall(resp)[0]


http.HTTPClient.get_api_key = get_api_key_patched

_log.debug("Monkey patch imported")
