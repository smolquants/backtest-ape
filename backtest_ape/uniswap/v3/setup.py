from typing import List

from ape import project
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance


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
    tokens: List[ContractInstance],
    fee: int,
    price: int,
    acc: AccountAPI,
) -> ContractInstance:
    """
    Creates mock Uniswap V3 pool through factory.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    [tokenA, tokenB] = tokens
    receipt = factory.createPool(tokenA.address, tokenB.address, fee, sender=acc)
    pool_addr = receipt.return_value
    pool = project.MockUniswapV3Pool.at(pool_addr)

    # initialize the pool prior to returning
    sqrt_price_x96 = int((price) ** (1 / 2)) << 96
    pool.initialize(sqrt_price_x96, sender=acc)
    return pool
