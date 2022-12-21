import click

from backtest_ape.base import BaseRunner
from backtest_ape.utils import get_test_account

from backtest_ape.uniswap.v3.setup import (
    deploy_mock_erc20,
    deploy_mock_position_manager,
    deploy_mock_univ3_factory,
    create_mock_pool,
)


class BaseUniswapV3Runner(BaseRunner):
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

        self._mocks = {
            "weth": mock_weth,
            "token": mock_token,
            "factory": mock_factory,
            "manager": mock_manager,
            "pool": mock_pool,
        }
