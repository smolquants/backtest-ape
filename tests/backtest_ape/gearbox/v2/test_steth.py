import os

import numpy as np
import pandas as pd
import pytest

from backtest_ape.gearbox.v2.steth import GearboxV2STETHRunner


@pytest.fixture
def runner():
    return GearboxV2STETHRunner(
        ref_addrs={
            "manager": "0x5887ad4Cb2352E7F01527035fAa3AE0Ef2cE2b9B",
            "adapter": "0x2aed5E59E3730d88c8a1d0C25A50a239DeF70275",
        },
        collateral_amount=100000000000000000000,  # 100 WETH
        leverage_factor=400,  # 400 WETH borrow
    )


@pytest.fixture
def path():
    p = "tests/results/gearbox/v2/steth.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner):
    number = 16254713
    state = runner.get_refs_state(number)
    expect = [
        (
            92233720368547797298,
            121963000000,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
        (
            92233720368547797298,
            120786558687,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
    ]
    assert state["feeds"] == expect


# TODO: fix for new gearbox lido adapter
@pytest.mark.skip
def test_init_mocks_state(runner, WETH9, STETH):
    runner.setup()
    state_feeds = [
        (
            92233720368547797298,
            121963000000,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
        (
            92233720368547797298,
            120786558687,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
    ]
    state = {"feeds": state_feeds}
    runner.init_mocks_state(state)

    # check mock price feeds added for collaterals
    price_oracle = runner._refs["price_oracle"]
    collaterals = runner._refs["collaterals"]
    for i, collateral in enumerate(collaterals):
        mock_feed = runner._mocks["feeds"][i]
        feed_addr = price_oracle.priceFeeds(collateral.address)
        assert mock_feed.address == feed_addr

    # check mocks init'd and backtester contract entered into stETH position
    manager = runner._refs["manager"]
    credit_account_addr = manager.creditAccounts(runner.backtester.address)
    assert WETH9.allowance(runner.backtester.address, manager.address) == 2**256 - 1
    assert STETH.balanceOf(credit_account_addr) == pytest.approx(500000000000000000000)


def test_set_mocks_state(runner):
    runner.setup()
    state_feeds = [
        (
            92233720368547797298,
            121963000000,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
        (
            92233720368547797298,
            120786558687,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
    ]
    state = {"feeds": state_feeds}
    runner.set_mocks_state(state)

    # check relevant mock feeds updated to given state
    for i, mock_feed in enumerate(runner._mocks["feeds"]):
        state_feed = state_feeds[i]
        if state_feed == tuple():
            assert mock_feed.latestRoundId() == 0
            continue

        assert mock_feed.latestRoundId() == state_feed[0]
        assert mock_feed.latestRoundData() == state_feed


def test_record(runner, path):
    runner.setup()
    number = 16254713
    state_feeds = [
        (
            92233720368547797298,
            121963000000,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
        (
            92233720368547797298,
            120786558687,
            1671882923,
            1671882923,
            92233720368547797298,
        ),
    ]
    state = {"feeds": state_feeds}
    value = 100000000000000000  # 1e18
    runner.record(path, number, state, value)

    # check pd dataframe has new row
    df = pd.read_csv(path)
    np.testing.assert_equal(
        list(df.columns),
        ["number", "value", "ETH / USD", "STETH / ETH ETH/USD Composite"],
    )

    row = df.iloc[0]
    assert int(row["number"]) == int(number)
    assert int(row["value"]) == int(value)
    assert int(row["ETH / USD"]) == int(state["feeds"][0][1])
    assert int(row["STETH / ETH ETH/USD Composite"]) == int(state["feeds"][1][1])
