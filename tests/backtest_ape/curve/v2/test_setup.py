from ape.contracts import ContractInstance
from backtest_ape.curve.v2.setup import (
    deploy_mock_lp,
)


def test_deploy_mock_lp(acc):
    tok = deploy_mock_lp("Mock Curve Token", "crv3m", acc)
    assert type(tok) == ContractInstance
    assert tok.name() == "Mock Curve Token"
    assert tok.symbol() == "crv3m"

    # try minting
    receipt = tok.mint(acc.address, 1000, sender=acc)
    assert receipt.return_value is True
    assert tok.balanceOf(acc) == 1000

    # try relative minting
    frac = 10000000000000000  # 1e16 == 1% of supply
    receipt = tok.mint_relative(acc.address, frac, sender=acc)
    assert receipt.return_value == 10
    assert tok.balanceOf(acc) == 1010

    # try burning
    receipt = tok.burnFrom(acc.address, 100, sender=acc)
    assert receipt.return_value is True
    assert tok.balanceOf(acc) == 910


def test_deploy_mock_pool(acc):
    pass
