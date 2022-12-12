import pytest

from ape import project


@pytest.fixture(scope="module")
def acc(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def backtest(acc):
    yield project.MockBacktest.deploy(sender=acc)
