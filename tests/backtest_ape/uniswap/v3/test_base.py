import pytest

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner


@pytest.fixture
def runner():
    return BaseUniswapV3Runner(
        ref_addrs={"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}
    )


def test_setup(runner, acc):
    runner.setup()
    assert runner._acc == acc

    mocks = runner._mocks
    assert set(mocks.keys()) == set(
        [
            "weth",
            "token",
            "factory",
            "manager",
            "pool",
        ]
    )
    assert mocks["weth"].symbol() == "WETH"
    assert mocks["token"].symbol() == "MOK"
    assert mocks["factory"].feeAmountTickSpacing(3000) == 60
    assert mocks["manager"].factory() == mocks["factory"].address
    assert mocks["pool"].fee() == 3000
    assert (
        mocks["factory"].getPool(mocks["weth"].address, mocks["token"].address, 3000)
        == mocks["pool"].address
    )
