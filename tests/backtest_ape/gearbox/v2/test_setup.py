from ape.contracts import ContractInstance

from backtest_ape.gearbox.v2.setup import deploy_mock_feed


def test_deploy_mock_feed(acc):
    feed = deploy_mock_feed("Mock Feed", 6, 1, acc)
    assert isinstance(feed, ContractInstance) is True
    assert feed.description() == "Mock Feed"
    assert feed.decimals() == 6
    assert feed.version() == 1

    # try setting a round of data in feed
    round = (1, 1000000, 1676127515, 1676127527, 1)
    feed.setRound(round, sender=acc)
    assert feed.rounds(1) == round
