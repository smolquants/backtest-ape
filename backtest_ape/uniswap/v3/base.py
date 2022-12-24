import click

from ape import Contract
from backtest_ape.base import BaseRunner
from backtest_ape.setup import deploy_mock_erc20
from backtest_ape.utils import get_test_account
from backtest_ape.uniswap.v3.setup import (
    deploy_mock_position_manager,
    deploy_mock_univ3_factory,
    create_mock_pool,
)
from typing import Any, ClassVar, List


class BaseUniswapV3Runner(BaseRunner):
    _ref_keys: ClassVar[List[str]] = ["pool"]

    def __init__(self, **data: Any):
        """
        Overrides BaseRunner init to also store ape Contract instances
        for tokens in ref pool.
        """
        super().__init__(**data)

        # store token contracts in _refs
        pool = self._refs["pool"]
        self._refs["tokens"] = [Contract(pool.token0()), Contract(pool.token1())]

    def setup(self):
        """
        Sets up Uniswap V3 runner for testing.

        Deploys mock ERC20 tokens needed for pool, mock Uniswap V3 factory
        and mock Uniswap V3 position manager. Deploys the mock pool
        through the factory.
        """
        acc = get_test_account()
        self._acc = acc

        # deploy the mock erc20s
        click.echo("Deploying mock ERC20 tokens ...")
        mock_tokens = [
            deploy_mock_erc20(f"Mock Token{i}", token.symbol(), token.decimals(), acc)
            for i, token in enumerate(self._refs["tokens"])
        ]

        # deploy weth if necessary
        mock_weth = (
            mock_tokens[0] if mock_tokens[0].symbol() == "WETH" else mock_tokens[1]
        )
        if mock_weth.symbol() != "WETH":
            mock_weth = deploy_mock_erc20("Mock WETH9", "WETH", 18, acc)

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
            mock_tokens,
            fee,
            price,
            acc,
        )

        self._mocks = {
            "tokens": mock_tokens,
            "factory": mock_factory,
            "manager": mock_manager,
            "pool": mock_pool,
        }
