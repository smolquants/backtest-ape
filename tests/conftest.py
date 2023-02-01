import pytest
from ape import accounts, Contract


@pytest.fixture(scope="session")
def acc(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def WETH9():
    yield Contract("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="session")
def bridge():
    yield accounts["0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1"]
