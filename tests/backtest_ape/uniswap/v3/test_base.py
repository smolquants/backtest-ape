import pytest

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner


@pytest.fixture
def runner():
    return BaseUniswapV3Runner(
        ref_addrs={
            "pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
            "manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        }
    )


def test_setup(runner):
    runner.setup()

    mocks = runner._mocks
    assert set(mocks.keys()) == set(
        [
            "tokens",
            "factory",
            "manager",
            "pool",
        ]
    )
    assert [token.address for token in runner._refs["tokens"]] == [
        runner._refs["pool"].token0(),
        runner._refs["pool"].token1(),
    ]
    assert set([token.symbol() for token in mocks["tokens"]]) == set(["WETH", "USDC"])
    assert [token.address for token in mocks["tokens"]] == [
        mocks["pool"].token0(),
        mocks["pool"].token1(),
    ]
    assert mocks["factory"].feeAmountTickSpacing(3000) == 60
    assert mocks["manager"].factory() == mocks["factory"].address
    assert mocks["pool"].fee() == 3000
    assert (
        mocks["factory"].getPool(
            mocks["tokens"][0].address, mocks["tokens"][1].address, 3000
        )
        == mocks["pool"].address
    )
    assert (
        mocks["pool"].slot0().sqrtPriceX96 == runner._refs["pool"].slot0().sqrtPriceX96
    )
