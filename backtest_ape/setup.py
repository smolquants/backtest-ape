from ape import project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI


def deploy_mock_erc20(
    name: str, symbol: str, decimals: int, acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock ERC20 token.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockERC20.deploy(name, symbol, decimals, sender=acc)
