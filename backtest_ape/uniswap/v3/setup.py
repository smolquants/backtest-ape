from typing import List

from ape import project
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance
from ape.utils import ZERO_ADDRESS


def deploy_mock_univ3_factory(acc: AccountAPI) -> ContractInstance:
    """
    Deploys mock Uniswap V3 factory.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockUniswapV3Factory.deploy(sender=acc)


def deploy_mock_position_manager(
    factory: ContractInstance, weth: ContractInstance, acc: AccountAPI
) -> ContractInstance:
    """
    Deploys mock NFT position manager.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockNonfungiblePositionManager.deploy(
        factory.address, weth.address, ZERO_ADDRESS, sender=acc
    )


def create_mock_pool(
    factory: ContractInstance,
    tokens: List[ContractInstance],
    fee: int,
    sqrt_price_x96: int,
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
    pool.initialize(sqrt_price_x96, sender=acc)
    return pool
