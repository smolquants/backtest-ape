import pytest

from backtest_ape.curve.v2.lp import CurveV2LPRunner


@pytest.fixture
def runner():
    amount_usd = int(1e24)
    amount_weth = int(1e24 * 1220)
    amount_wbtc = int(1e24 * 16834)
    return CurveV2LPRunner(
        amounts=[
            amount_usd,  # USDM
            amount_wbtc,  # MOK (WBTC)
            amount_weth,  # WETH
        ]
    )


def test_init_mocks_state(runner):
    pass


def test_get_refs_state(runner):
    pass
