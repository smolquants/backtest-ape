def test_execute(backtest, acc):
    pass


def test_multicall(backtest, acc):
    pass


def test_value(backtest, acc):
    assert backtest.value() == 0

    # send 1 eth in to backtester
    acc.transfer(backtest.address, 1000000000000000000)  # 1 wad
    assert backtest.value() == 1000000000000000000
