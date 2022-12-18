import pytest

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner


@pytest.fixture
def runner():
    return BaseUniswapV3Runner()


def test_setup(runner):
    runner.setup()
    assert runner._initialized is True

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
