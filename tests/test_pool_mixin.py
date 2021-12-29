import pytest

from steam_tradeoffer_manager.base import PoolBotMixin


class PoolSubclass(PoolBotMixin):
    class Pool:
        ...

    def __init__(self):
        self._id = 123
        self._pool = PoolSubclass.Pool()


@pytest.fixture
def pool_sub_instance():
    return PoolSubclass()


def test_pool_mixin_id_property(pool_sub_instance):
    assert pool_sub_instance.id == 123


def test_pool_mixin_pool_property(pool_sub_instance):
    assert isinstance(pool_sub_instance.pool, PoolSubclass.Pool)
