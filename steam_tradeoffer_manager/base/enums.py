import enum
from random import randint, random
from typing import Callable

__all__ = ('BotState', 'ONCE_EVERY')


class BotState(enum.Enum):
    Active = 'active'  # working fine
    Waiting = 'waiting'  # waiting until ready
    InvalidCredentials = 'invalid credentials'
    UnknownError = 'unknown exception'  # stopped by error
    Stopped = 'stopped'  # just stopped


class Timings:
    @staticmethod
    def _randomizer(*_range: int) -> Callable[[...], int]:
        return lambda *a, **ka: round(randint(*_range) * 60 * 60 + (random() * 60 * 60))

    @classmethod
    def custom(cls, from_: int, to: int) -> Callable[[...], int]:
        return cls._randomizer(from_, to)

    HOUR = _randomizer(0, 1)  # not recommended
    TWO_HOURS = _randomizer(1, 1)  # not recommended
    FOUR_HOURS = _randomizer(2, 3)
    SIX_HOURS = _randomizer(4, 5)
    EIGHT_HOURS = _randomizer(6, 7)
    HALF_A_DAY = _randomizer(10, 11)
    DAY = _randomizer(21, 23)
    TWO_DAYS = _randomizer(39, 47)  # not recommended


ONCE_EVERY = Timings
