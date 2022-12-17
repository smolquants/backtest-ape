from ape.contracts import ContractInstance
from backtest_ape.uniswap.v3 import utils


def test_deploy_mock_erc20(acc):
    tok = utils.deploy_mock_erc20("Mock Token", "MOK", acc)
    assert type(tok) == ContractInstance
    assert tok.name() == "Mock Token"
    assert tok.symbol() == "MOK"

    # try minting
    tok.mint(acc.address, 1000, sender=acc)
    assert tok.balanceOf(acc) == 1000

    # try burning
    tok.burn(acc.address, 100, sender=acc)
    assert tok.balanceOf(acc) == 900


def test_deploy_mock_univ3_factory(acc):
    factory = utils.deploy_mock_univ3_factory(acc)
    assert type(factory) == ContractInstance
    assert factory.owner() == acc.address
    assert factory.feeAmountTickSpacing(500) == 10
    assert factory.feeAmountTickSpacing(3000) == 60
    assert factory.feeAmountTickSpacing(10000) == 200
