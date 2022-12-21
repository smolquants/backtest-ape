import pytest

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner


@pytest.fixture
def runner():
    return BaseUniswapV3Runner(
        ref_addrs={
            "pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
            "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        }
    )


def test_setup(runner, acc):
    runner.setup()
    assert runner._acc == acc

    mocks = runner._mocks
    assert set(mocks.keys()) == set(
        [
            "tokenA",
            "tokenB",
            "factory",
            "manager",
            "pool",
        ]
    )
    assert mocks["tokenA"].symbol() == "MOKA"
    assert mocks["tokenB"].symbol() == "MOKB"
    assert mocks["factory"].feeAmountTickSpacing(3000) == 60
    assert mocks["manager"].factory() == mocks["factory"].address
    assert mocks["pool"].fee() == 3000
    assert (
        mocks["factory"].getPool(mocks["tokenA"].address, mocks["tokenB"].address, 3000)
        == mocks["pool"].address
    )
