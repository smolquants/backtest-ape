import click

from backtest_ape.base import BaseRunner
from backtest_ape.setup import deploy_mock_erc20
from backtest_ape.utils import get_test_account
from backtest_ape.curve.v2.setup import deploy_mock_pool
from typing import Any


class BaseCurveV2Runner(BaseRunner):
    def __init__(self, **data: Any):
        """
        Overrides BaseRunner init to check ref_addrs contains
        pool.
        """
        super().__init__(**data)
        ks = ["pool"]  # TODO: use pydantic validators with ref in base runner
        for k in ks:
            if k not in self._refs.keys():
                raise ValueError(f"ref_addrs does not contain key '{k}'.")

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
        mock_weth = deploy_mock_erc20("WETH9", "WETH", acc)
        mock_token = deploy_mock_erc20("Mock ERC20", "MOK", acc)

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
            [mock_usd, mock_weth, mock_token],
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
            "weth": mock_weth,
            "token": mock_token,
            "pool": mock_pool,
        }
