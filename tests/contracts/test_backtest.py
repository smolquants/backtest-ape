def test_execute(backtest, WETH9, acc):
    # deposit 1 eth to WETH through backtester
    target = WETH9.address
    data = WETH9.deposit.as_transaction().data
    val = 1000000000000000000  # 1 wad
    prior_acc_bal = acc.balance

    # execute deposit through backtester
    receipt = backtest.execute(target, data, val, value=val, sender=acc)

    # check backtester credited with 1 WETH
    assert WETH9.balanceOf(backtest) == val

    # check no balance of eth in backtester
    assert backtest.balance == 0

    # check the eth came from acc
    assert acc.balance == prior_acc_bal - val - receipt.total_fees_paid


def test_multicall(backtest, WETH9, acc):
    # deposit 1 eth to WETH then withdraw 1 WETH to backtester
    targets = [WETH9.address, WETH9.address]
    datas = [
        WETH9.deposit.as_transaction().data,
        WETH9.withdraw.as_transaction(1000000000000000000).data,
    ]
    values = [1000000000000000000, 0]  # 1 wad
    tv = sum(values)
    prior_acc_bal = acc.balance

    # multicall deposit => withdraw through backtester
    receipt = backtest.multicall(targets, datas, values, value=tv, sender=acc)

    # check no balance of WETH in backtester
    assert WETH9.balanceOf(backtest) == 0

    # check backtester credited with 1 ETH
    assert backtest.balance == tv

    # check the eth came from acc
    assert acc.balance == prior_acc_bal - tv - receipt.total_fees_paid


def test_value(backtest, acc):
    assert backtest.value() == 0

    # send 1 eth in to backtester
    acc.transfer(backtest.address, 1000000000000000000)  # 1 wad
    assert backtest.value() == 1000000000000000000
