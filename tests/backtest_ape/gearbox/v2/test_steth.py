import os

import numpy as np
import pandas as pd
import pytest

from backtest_ape.gearbox.v2.steth import GearboxV2STETHRunner


@pytest.fixture
def runner():
    # TODO: amount and leverage
    return GearboxV2STETHRunner(
        ref_addrs={"manager": "0x5887ad4Cb2352E7F01527035fAa3AE0Ef2cE2b9B"},
    )


@pytest.fixture
def path():
    p = "tests/results/gearbox/v2/steth.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner, WETH9, STETH):
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
    expect += [tuple() for _ in range(len(runner._refs["feeds"]) - 2)]
    assert state["feeds"] == expect


def test_init_mocks_state(runner):
    pass


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
    state_feeds += [tuple() for _ in range(len(runner._refs["feeds"]) - 2)]
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
    state_feeds += [tuple() for _ in range(len(runner._refs["feeds"]) - 2)]
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
