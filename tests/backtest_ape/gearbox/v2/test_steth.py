import os

import pytest

from backtest_ape.gearbox.v2.steth import GearboxV2STETHRunner


@pytest.fixture
def runner():
    # TODO: amount and leverage
    return GearboxV2STETHRunner(
        ref_addrs={"manager": "0x5887ad4Cb2352E7F01527035fAa3AE0Ef2cE2b9B"},
    )


@pytest.fixture
def path():
    p = "tests/results/gearbox/v2/steth.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner):
    # number = 16254713
    pass


def test_init_mocks_state(runner):
    pass


def test_set_mocks_state(runner):
    pass


def test_record(runner, path):
    pass
