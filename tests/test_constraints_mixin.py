import pytest

from steam_tradeoffer_manager.base.exceptions import ConstraintException
from steam_tradeoffer_manager.base import ConstraintsMixin


@pytest.fixture
def get_c():
    class ConstraintsSubclass(ConstraintsMixin):
        constraints = ("arg1", ("arg2", "arg3"))
        dimension = "test_dimension"

        def __init__(self, arg1, arg2, arg3): ...

    return ConstraintsSubclass


def test_coupled_constraint(get_c):
    c = get_c("1", "2", arg3="3")
    c1 = get_c("2", "2", arg3="4")
    assert c and c1


def test_lonely_constraint(get_c):
    c = get_c("1", "2", arg3="3")
    with pytest.raises(ConstraintException):
        c1 = get_c("1", arg2="3", arg3="3")


def test_mixin_constraint_work(get_c):
    c = get_c("1", "2", "3")
    with pytest.raises(ConstraintException):
        c = get_c("1", "2", "3")


def test_mixin_constraint_hash_clearing(get_c):
    c = get_c("1", "2", arg3="3")
    c.__del__()
    c = get_c("1", "2", arg3="3")
