from ape import project
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance


def deploy_mock_feed(
    description: str, decimals: int, version: int, acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock Chainlink feed.

    Args:
        description (str): Description of the oracle.
        decimals (int): Number of decimals associated with the oracle.
        version (int): Version number oracle is on.
        acc (AccountAPI): Account to deploy the mock oracle.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """

    return project.MockAggregatorV3.deploy(description, decimals, version, sender=acc)
