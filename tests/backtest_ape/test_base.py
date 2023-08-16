from contextlib import contextmanager

import pytest
from ape import Contract, chain, networks

from backtest_ape.base import BaseRunner


# SEE: https://github.com/ApeWorX/ape-foundry/blob/main/tests/conftest.py#L52
@contextmanager
def _isolate():
    if networks.active_provider is None:
        raise AssertionError("Isolation should only be used with a connected provider.")

    init_network_name = chain.provider.network.name
    if init_network_name != "mainnet-fork":
        raise AssertionError(
            "Isolation should only be used with network `mainnet-fork`."
        )

    init_number = chain.blocks.head.number

    yield

    chain.provider.reset_fork(init_number)


@pytest.fixture(autouse=True)
def reset_fork_isolation():
    with _isolate():
        yield


class Runner(BaseRunner):
    _ref_keys = ["pool"]


@pytest.fixture
def number():
    return 16513664


@pytest.fixture
def ref_addrs():
    return {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}


@pytest.fixture
def runner(ref_addrs):
    return Runner(ref_addrs=ref_addrs)


def test_init(acc):
    ref_addrs = {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}
    runner = BaseRunner(ref_addrs=ref_addrs)
    assert runner._refs == {
        "pool": Contract("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    }
    assert runner._acc == acc


def test_init_when_acc_not_none(bridge, acc):
    ref_addrs = {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}
    runner = BaseRunner(ref_addrs=ref_addrs, acc_addr=bridge.address)
    assert runner._acc == bridge
    assert runner._acc.balance == acc.balance


def test_validator_when_has_keys():
    Runner(ref_addrs={"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"})


def test_validator_when_not_has_keys():
    with pytest.raises(ValueError):
        Runner(ref_addrs={})


def test_reset_fork(number, runner):
    transactions = chain.blocks[number + 1].transactions
    base_fee = chain.blocks[number].base_fee

    runner.reset_fork(number)
    assert chain.blocks.head.number == number
    chain.provider.send_transaction(transactions[0])
    assert chain.blocks.head.base_fee == base_fee


def test_get_ref_txs(number, runner):
    transactions = chain.blocks[number].transactions
    runner.reset_fork(number - 1)

    ref_txs = runner.get_ref_txs(number)
    assert ref_txs == transactions


def test_submit_tx(number, runner, WETH9):
    transactions = chain.blocks[number].transactions
    runner.reset_fork(number - 1)

    # cache WETH9 balance of pool swap thru in tx
    pool_addr = "0xC1409A2c5673299fB15Da5f03c27EB1aC88f7D8C"
    pool_weth_bal_prior = WETH9.balanceOf(pool_addr)

    # SEE: https://etherscan.io/tx/0xdd05e6aa918593db4c777723efbdd55fbd92e0d213f43b6013d97885fc2abe23  # noqa: E501
    tx = transactions[114]  # know this does *not* revert
    runner.submit_tx(tx)
    assert chain.blocks[number].transactions == [tx]

    # check Uni V3 swap tx altered pool balance of WETH9
    pool_weth_bal_post = WETH9.balanceOf(pool_addr)
    actual_delta_bal = pool_weth_bal_prior - pool_weth_bal_post
    expect_delta_bal = 85681526175119496
    assert actual_delta_bal == expect_delta_bal


# TODO: fix
@pytest.mark.skip
def test_submit_txs(number, runner):
    transactions = chain.blocks[number].transactions
    runner.reset_fork(number - 1)

    print("transactions", transactions)

    txs = transactions[1:10]  # know all of these do *not* revert

    print("txs", txs)

    runner.submit_txs(txs)

    print("number", number)

    # check each tx in txs submitted in separate block or passed due to silent fail
    # TODO: fix silent fail case
    for i in range(len(txs)):
        assert chain.blocks[number + i].transactions == [txs[i]]


def test_submit_tx_when_reverts(number, runner):
    transactions = chain.blocks[number].transactions
    runner.reset_fork(number - 1)

    # check reverted tx included in block (fails silently)
    tx = transactions[84]  # know this *does* revert
    runner.submit_tx(tx)
    assert chain.blocks[number].transactions == [tx]


# TODO: test_backtest, test_replay, test_forwardtest
