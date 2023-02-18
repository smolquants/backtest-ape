from typing import ClassVar, List

import pytest

from backtest_ape.gearbox.v2.base import BaseGearboxV2Runner


class Runner(BaseGearboxV2Runner):
    collateral_addrs: ClassVar[List[str]] = [
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    ]


@pytest.fixture
def runner():
    return Runner(
        ref_addrs={
            "manager": "0x5887ad4Cb2352E7F01527035fAa3AE0Ef2cE2b9B",
        },
    )


def test_setup(runner):
    runner.setup()

    # check mock feeds
    mocks = runner._mocks
    assert set(mocks.keys()) == set(["feeds"])
    assert len(mocks["feeds"]) == len(runner._refs["feeds"])
    assert [feed.description() for feed in mocks["feeds"]] == [
        feed.description() for feed in runner._refs["feeds"]
    ]
    assert [feed.decimals() for feed in mocks["feeds"]] == [
        feed.decimals() for feed in runner._refs["feeds"]
    ]
    assert [feed.version() for feed in mocks["feeds"]] == [
        feed.version() for feed in runner._refs["feeds"]
    ]
