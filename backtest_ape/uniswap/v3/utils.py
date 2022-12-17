import click

from ape import project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI
from typing import Mapping


def deploy_mock_erc20(name: str, symbol: str, acc: AccountAPI) -> ContractInstance:
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
    deployer = project.MockUniswapV3PoolDeployer.deploy(sender=acc)
    return project.MockUniswapV3Factory.deploy(deployer.address, sender=acc)


def deploy_mock_position_manager(
    factory: ContractInstance, weth: ContractInstance, acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock NFT position manager.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockNonfungiblePositionManager.deploy(
        factory.address, weth.address, sender=acc
    )


def create_mock_pool(
    factory: ContractInstance,
    tokenA: ContractInstance,
    tokenB: ContractInstance,
    fee: int,
    price: int,
    acc: AccountAPI,
) -> ContractInstance:
    receipt = factory.createPool(tokenA.address, tokenB.address, fee, sender=acc)
    pool_addr = receipt.return_value
    pool = project.MockUniswapV3Pool.at(pool_addr)

    # initialize the pool prior to returning
    sqrt_price_x96 = int((price) ** (1 / 2)) << 96
    pool.initialize(sqrt_price_x96, sender=acc)
    return pool


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
    mock_weth = deploy_mock_erc20("WETH9", "WETH", acc)
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
    price = 1000000000000000000  # 1 wad
    mock_pool = create_mock_pool(
        mock_factory,
        mock_weth,
        mock_token,
        fee,
        price,
        acc,
    )

    return {
        "weth": mock_weth,
        "token": mock_token,
        "factory": mock_factory,
        "manager": mock_manager,
        "pool": mock_pool,
    }
