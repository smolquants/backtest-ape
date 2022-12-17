import click

from ape import project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI
from typing import Mapping


def deploy_mock_erc20(
    name: str,
    symbol: str,
    acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock ERC20 token.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockERC20.deploy(name, symbol, sender=acc)


def deploy_mock_univ3_factory(acc: AccountAPI) -> ContractInstance:
    """
    Deploys mock Uniswap V3 factory.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockUniswapV3Factory.deploy(sender=acc)


def deploy_mock_position_manager(
    factory: ContractInstance,
    weth: ContractInstance,
    acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock NFT position manager.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockNonfungiblePositionManager.deploy(
        factory.address,
        weth.address,
        sender=acc
    )


def create_mock_pool(
    factory: ContractInstance,
    tokenA: ContractInstance,
    tokenB: ContractInstance,
    fee: int,
    acc: AccountAPI
) -> ContractInstance:
    receipt = factory.createMockPool(
        tokenA.address,
        tokenB.address,
        fee,
        sender=acc
    )
    pool_addr = receipt.return_value
    return project.MockUniswapV3Pool.at(pool_addr)


def setup(acc: AccountAPI) -> Mapping[str, ContractInstance]:
    """
    Initial setup for Uniswap V3 backtesters.

    Deploys mock ERC20 tokens needed for pool, mock Uniswap V3 factory
    and mock Uniswap V3 position manager. Deploys the mock pool
    through the factory. Then returns the NFT position manager instance.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    # deploy the mock erc20s
    click.echo("Deploying mock ERC20 tokens ...")
    mock_weth = deploy_mock_erc20("Wrapped Ether", "WETH", acc)
    mock_token = deploy_mock_erc20("Mock ERC20", "MOK", acc)

    # deploy the mock univ3 factory
    click.echo("Deploying mock Uniswap V3 factory ...")
    mock_factory = deploy_mock_univ3_factory(acc)

    # deploy the mock NFT position manager
    # NOTE: uses zero address for descriptor so tokenURI will fail
    click.echo("Deploying the mock position manager ...")
    mock_manager = deploy_mock_position_manager(mock_factory, mock_weth, acc)

    # create the pool through the mock univ3 factory
    fee = 3000  # default fee of 0.3%
    mock_pool = create_mock_pool(mock_factory, mock_weth, mock_token, fee, acc)

    return {
        "mock_weth": mock_weth,
        "mock_token": mock_token,
        "mock_factory": mock_factory,
        "mock_manager": mock_manager,
        "mock_pool": mock_pool,
    }