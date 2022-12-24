import pytest

from backtest_ape.curve.v2.lp import CurveV2LPRunner


@pytest.fixture
def runner():
    amount_usd = int(1e24)
    amount_weth = int(1e24 * 1220)
    amount_wbtc = int(1e24 * 16834)
    return CurveV2LPRunner(
        ref_addrs={"pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"},
        num_coins=3,
        amounts=[
            amount_usd,  # USDT
            amount_wbtc,  # WBTC
            amount_weth,  # WETH
        ],
    )


def test_get_refs_state(runner):
    number = 16254713
    state = runner.get_refs_state(number)
    assert state["balances"] == [51444788313173, 306130683764, 42421274934619665540607]
    assert state["D"] == 154655480528709339739900799
    assert state["A_gamma"] == [
        183752478137306770270222288013175834186240000,
        581076037942835227425498917514114728328226821,
        1633548703,
        0,
    ]
    assert state["prices"] == [
        16816946825680501806263,
        1218668363989192860592,
    ]


def test_init_mocks_state(runner):
    pass
