import pytest

from backtest_ape.curve.v2.base import BaseCurveV2Runner


@pytest.fixture
def runner():
    return BaseCurveV2Runner(
        ref_addrs={"pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"}
    )


def test_setup(runner, acc):
    runner.setup()
    assert runner._acc == acc

    mocks = runner._mocks
    assert set(mocks.keys()) == set(
        [
            "usd",
            "weth",
            "token",
            "lp",
            "pool",
        ]
    )
    assert mocks["usd"].symbol() == "USDM"
    assert mocks["weth"].symbol() == "WETH"
    assert mocks["token"].symbol() == "MOK"
    assert mocks["pool"].A() == 1000000
    assert [mocks["pool"].coins(i) for i in range(3)] == [
        mocks["usd"].address,
        mocks["weth"].address,
        mocks["token"].address,
    ]
    assert mocks["pool"].token() == mocks["lp"].address
