import os

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
    pass
