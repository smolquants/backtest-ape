from ape.contracts import ContractInstance

from backtest_ape.setup import deploy_mock_erc20


def test_deploy_mock_erc20(acc):
    tok = deploy_mock_erc20("Mock Token", "MOK", 18, acc)
    assert isinstance(tok, ContractInstance) is True
    assert tok.name() == "Mock Token"
    assert tok.symbol() == "MOK"
    assert tok.decimals() == 18

    # try minting
    tok.mint(acc.address, 1000, sender=acc)
    assert tok.balanceOf(acc) == 1000

    # try burning
    tok.burn(acc.address, 100, sender=acc)
    assert tok.balanceOf(acc) == 900
