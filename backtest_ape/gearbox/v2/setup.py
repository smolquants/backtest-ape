from ape import project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI


def deploy_mock_feed(
    decimals: int, description: str, version: int, acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock Chainlink feed.

    Args:
        decimals (int): Number of decimals associated with the oracle.
        description (str): Description of the oracle.
        version (int): Version number oracle is on.
        acc (AccountAPI): Account to deploy the mock oracle.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockAggregatorV3.deploy(decimals, description, version, sender=acc)
