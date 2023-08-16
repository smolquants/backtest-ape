import pytest
from ape import Contract, accounts, project


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
    yield project.WETH9.at("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


@pytest.fixture(scope="session")
def STETH():
    yield Contract("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")


@pytest.fixture(scope="session")
def bridge():
    yield accounts["0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf"]
