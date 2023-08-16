import ape
import numpy as np
import pytest
from ape.contracts import ContractInstance

from backtest_ape.setup import deploy_mock_erc20
from backtest_ape.uniswap.v3.setup import (
    create_mock_pool,
    deploy_mock_position_manager,
    deploy_mock_univ3_factory,
)


def test_deploy_mock_univ3_factory(acc):
    factory = deploy_mock_univ3_factory(acc)
    assert isinstance(factory, ContractInstance) is True
    assert factory.owner() == acc.address
    assert factory.feeAmountTickSpacing(500) == 10
    assert factory.feeAmountTickSpacing(3000) == 60
    assert factory.feeAmountTickSpacing(10000) == 200


def test_deploy_mock_position_manager(acc):
    factory = deploy_mock_univ3_factory(acc)
    weth = deploy_mock_erc20("WETH9", "WETH", 18, acc)
    manager = deploy_mock_position_manager(factory, weth, acc)
    assert isinstance(manager, ContractInstance) is True
    assert manager.factory() == factory.address
    assert manager.WETH9() == weth.address

    with ape.reverts("Invalid token ID"):
        _ = manager.positions(0)


@pytest.mark.parametrize("fee", [500, 3000, 10000])
def test_create_mock_pool(acc, fee):
    factory = deploy_mock_univ3_factory(acc)
    tokenA = deploy_mock_erc20("Token A", "TOKA", 18, acc)
    tokenB = deploy_mock_erc20("Token B", "TOKB", 18, acc)
    tokens = [tokenA, tokenB]
    price = 1000000000000000000  # 1 wad

    pool = create_mock_pool(factory, tokens, fee, price, acc)
    assert pool.factory() == factory.address
    assert pool.fee() == fee
    assert pool.tickSpacing() == factory.feeAmountTickSpacing(fee)
    assert factory.getPool(tokenA.address, tokenB.address, fee) == pool.address

    token0 = pool.token0()
    token1 = pool.token1()
    assert set([token0, token1]) == set([tokenA.address, tokenB.address])

    slot0 = pool.slot0()
    assert slot0.sqrtPriceX96 == int((price) ** (1 / 2)) << 96
    np.testing.assert_allclose(
        slot0.tick,
        int(np.log(price) / np.log(1.0001)),
        atol=1,
    )
    assert slot0.observationIndex == 0
    assert slot0.observationCardinality == 1
    assert slot0.observationCardinalityNext == 1
    assert slot0.feeProtocol == 0
    assert slot0.unlocked is True
