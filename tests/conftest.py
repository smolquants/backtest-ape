import pytest

from ape import Contract, project


@pytest.fixture(scope="module")
def acc(accounts):
    yield accounts[0]


@pytest.fixture(scope="module")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="module")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def backtest(acc):
    yield project.MockBacktest.deploy(sender=acc)


@pytest.fixture(scope="module")
def setter(acc):
    yield project.MockSetter.deploy(sender=acc)


@pytest.fixture(scope="module")
def WETH9():
    yield Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
