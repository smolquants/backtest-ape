import ape
import pytest
import numpy as np

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


def test_deploy_mock_position_manager(acc):
    factory = utils.deploy_mock_univ3_factory(acc)
    weth = utils.deploy_mock_erc20("WETH9", "WETH", acc)
    manager = utils.deploy_mock_position_manager(factory, weth, acc)
    assert type(manager) == ContractInstance
    assert manager.factory() == factory.address
    assert manager.WETH9() == weth.address

    with ape.reverts("Invalid token ID"):
        _ = manager.positions(0)


@pytest.mark.parametrize("fee", [500, 3000, 10000])
def test_create_mock_pool(acc, fee):
    factory = utils.deploy_mock_univ3_factory(acc)
    tokenA = utils.deploy_mock_erc20("Token A", "TOKA", acc)
    tokenB = utils.deploy_mock_erc20("Token B", "TOKB", acc)
    price = 1000000000000000000  # 1 wad

    pool = utils.create_mock_pool(factory, tokenA, tokenB, fee, price, acc)
    assert pool.factory() == factory.address
    assert pool.fee() == fee
    assert pool.tickSpacing() == factory.feeAmountTickSpacing(fee)

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


def test_setup(acc):
    mocks = utils.setup(acc)
    assert set(mocks.keys()) == set(
        [
            "weth",
            "token",
            "factory",
            "manager",
            "pool",
        ]
    )
    assert mocks["weth"].symbol() == "WETH"
    assert mocks["token"].symbol() == "MOK"
    assert mocks["factory"].feeAmountTickSpacing(3000) == 60
    assert mocks["manager"].factory() == mocks["factory"].address
    assert mocks["pool"].fee() == 3000
