from ape import Contract
from backtest_ape.base import BaseRunner


def test_init():
    ref_addrs = {"pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"}
    runner = BaseRunner(ref_addrs=ref_addrs)
    assert runner._refs == {
        "pool": Contract("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8")
    }
