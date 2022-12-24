import click

from backtest_ape.base import BaseRunner
from backtest_ape.setup import deploy_mock_erc20
from backtest_ape.utils import get_test_account
from backtest_ape.curve.v2.setup import (
    deploy_mock_pool,
    deploy_mock_lp,
)
from typing import ClassVar, List


class BaseCurveV2Runner(BaseRunner):
    _ref_keys: ClassVar[List[str]] = ["pool"]

    def setup(self):
        """
        Sets up Curve V2 runner for testing.

        Deploys mock ERC20 tokens needed for pool and mock Curve V2 pool.
        """
        acc = get_test_account()
        self._acc = acc

        # deploy the mock erc20s
        click.echo("Deploying mock ERC20 tokens ...")
        mock_usd = deploy_mock_erc20("Mock USD", "USDM", acc)
        mock_token = deploy_mock_erc20("Mock ERC20", "MOK", acc)
        mock_weth = deploy_mock_erc20("WETH9", "WETH", acc)

        # deploy the mock lp token
        mock_lp = deploy_mock_lp("Mock Curve Tricrypto LP", "crv3m", acc)

        # deploy the mock curve v2 pool
        A = 1000000  # 10**6
        gamma = 10000000000000  # 10**13
        mid_fee = 5000000  # 5 bps
        out_fee = 30000000  # 3 bps
        allowed_extra_profit = 2000000000000  # 2 * 10**12
        fee_gamma = 500000000000000
        adjustment_step = 2000000000000000
        admin_fee = 5000000000
        ma_half_time = 600
        price = 1000000000000000000  # 1 wad
        mock_pool = deploy_mock_pool(
            [mock_usd, mock_token, mock_weth],
            mock_lp,
            A,
            gamma,
            mid_fee,
            out_fee,
            allowed_extra_profit,
            fee_gamma,
            adjustment_step,
            admin_fee,
            ma_half_time,
            [price, price],
            acc,
        )

        self._mocks = {
            "usd": mock_usd,
            "token": mock_token,
            "weth": mock_weth,
            "lp": mock_lp,
            "pool": mock_pool,
        }
