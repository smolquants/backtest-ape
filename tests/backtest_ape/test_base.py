import pytest
from ape import Contract, chain

from backtest_ape.base import BaseRunner


class Runner(BaseRunner):
    _ref_keys = ["pool"]


@pytest.fixture
def number():
    return 16513664


@pytest.fixture
def transactions(number):
    return chain.blocks[number].transactions


@pytest.fixture
def ref_addrs():
    return {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}


@pytest.fixture
def runner(ref_addrs):
    return Runner(ref_addrs=ref_addrs)


def test_init():
    ref_addrs = {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}
    runner = BaseRunner(ref_addrs=ref_addrs)
    assert runner._refs == {
        "pool": Contract("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    }


def test_validator_when_has_keys():
    Runner(ref_addrs={"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"})


def test_validator_when_not_has_keys():
    with pytest.raises(ValueError):
        Runner(ref_addrs={})


def test_load_ref_txs(number, transactions, runner):
    runner.load_ref_txs(number)
    assert runner._ref_txs[number] == transactions


def test_get_ref_txs(number, transactions, runner):
    runner.load_ref_txs(number)
    ref_txs = runner.get_ref_txs(number)
    assert ref_txs == transactions


def test_submit_tx(number, transactions, runner):
    head_number = chain.blocks.head.number
    chain.provider.reset_fork(number - 1)

    tx = transactions[0]  # know this does *not* revert
    runner.submit_tx(tx)
    assert chain.blocks[number].transactions == [tx]

    # NOTE: avoids BlockNotFound exceptions with isolation fixture
    chain.provider.reset_fork(head_number)


def test_submit_txs(number, transactions, runner):
    head_number = chain.blocks.head.number
    chain.provider.reset_fork(number - 1)

    txs = transactions[1:10]  # know all of these do *not* revert
    runner.submit_txs(txs)

    # check each tx in txs submitted in separate block
    for i in range(len(txs)):
        assert chain.blocks[number + i].transactions == [txs[i]]

    # NOTE: avoids BlockNotFound exceptions with isolation fixture
    chain.provider.reset_fork(head_number)


# TODO: test_backtest, test_replay, test_forwardtest
