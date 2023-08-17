import os

import pytest

from backtest_ape.uniswap.v3.lp import UniswapV3LPRunner


@pytest.fixture
def runner():
    tick_lower = 200280  # ~ 2000 * 1e6 USDC per 1e18 WETH
    tick_upper = 207240  # ~ 1000 * 1e6 USDC per 1e18 WETH
    amount_weth = 67000000000000000000  # 67 * 1e18 WETH
    amount_token = 100000000000  # 100,000 * 1e6 USDC
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


@pytest.fixture
def path():
    p = "tests/results/uniswap/v3/lp.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner):
    number = 16254713
    state = runner.get_refs_state(number)
    assert state["slot0"] == (
        2271115536847293636470521670171130,
        205279,
        785,
        1440,
        1440,
        0,
        True,
    )
    assert state["liquidity"] == 12591259481453220445
    assert state["fee_growth_global0_x128"] == 2888042077048564188809648235097692
    assert (
        state["fee_growth_global1_x128"] == 1330797012137927971917418324177509306984464
    )
    assert state["tick_info_lower"] == (
        230516823693049349,
        219847946486843875,
        1978179284235729126809955078548603,
        686326366930384297893016232932562090588936,
        6152462131364,
        198044337547992425673455364086492440599870,
        1651587340,
        True,
    )
    assert state["tick_info_upper"] == (
        3751134120809473278,
        -3747086165587011074,
        19987873086249178503837842262736,
        20984788605317380052250079237007968349421,
        17604723804,
        3779291462154278330045433,
        84814,
        True,
    )


def test_init_mocks_state(runner):
    pass


def test_set_mocks_state(runner):
    pass


def test_record(runner):
    pass
