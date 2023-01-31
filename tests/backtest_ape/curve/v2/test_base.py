import pytest

from backtest_ape.curve.v2.base import BaseCurveV2Runner


@pytest.fixture
def runner():
    return BaseCurveV2Runner(
        ref_addrs={"pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"},
        num_coins=3,
    )


def test_setup(runner):
    runner.setup()

    mocks = runner._mocks
    assert set(mocks.keys()) == set(
        [
            "coins",
            "lp",
            "pool",
        ]
    )
    assert set([coin.symbol() for coin in mocks["coins"]]) == set(
        ["USDT", "WBTC", "WETH"]
    )
    assert mocks["pool"].A() == 1000000
    assert set([mocks["pool"].coins(i) for i in range(runner.num_coins)]) == set(
        [coin.address for coin in mocks["coins"]]
    )
    assert mocks["pool"].token() == mocks["lp"].address
