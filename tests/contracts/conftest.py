import pytest
from ape import project


@pytest.fixture(scope="module")
def backtest(acc):
    yield project.MockBacktest.deploy(sender=acc)


@pytest.fixture(scope="module")
def setter(acc):
    yield project.MockSetter.deploy(sender=acc)
