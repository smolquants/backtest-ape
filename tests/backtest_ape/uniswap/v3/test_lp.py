import pytest

from backtest_ape.uniswap.v3.lp import UniswapV3LPRunner


@pytest.fixture
def runner():
    tick_lower = 0
    tick_upper = 0
    amount_weth = 0
    amount_token = 0
    return UniswapV3LPRunner(
        ref_addrs={
            "pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
            "manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        },
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount_weth=amount_weth,
        amount_token=amount_token,
    )
