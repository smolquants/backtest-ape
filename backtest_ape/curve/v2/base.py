from typing import Any, ClassVar, List

import click
from ape import Contract

from backtest_ape.base import BaseRunner
from backtest_ape.curve.v2.setup import deploy_mock_lp, deploy_mock_pool
from backtest_ape.setup import deploy_mock_erc20


class BaseCurveV2Runner(BaseRunner):
    num_coins: int = 0
    _ref_keys: ClassVar[List[str]] = ["pool"]

    def __init__(self, **data: Any):
        """
        Overrides BaseRunner init to also store ape Contract instances
        for tokens in ref pool.
        """
        super().__init__(**data)

        # store coin contracts in _refs
        pool = self._refs["pool"]
        self._refs["coins"] = [Contract(pool.coins(i)) for i in range(self.num_coins)]

        # check num coins matches pool
        matches = False
        try:
            self._refs["pool"].coins(self.num_coins)  # should error
        except Exception:
            matches = True

        if not matches:
            raise ValueError("num_coins not same as pool.N_COINS")

        # store pool lp token in _refs
        self._refs["lp"] = Contract(pool.token())

    def setup(self, mocking: bool = True):
        """
        Sets up Curve V2 runner for testing. Deploys mock ERC20 tokens needed
        for pool and mock Curve V2 pool, if mocking.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        if mocking:
            self.deploy_mocks()

    def deploy_mocks(self):
        """
        Deploys the mock contracts.
        """
        # deploy the mock erc20s
        click.echo("Deploying mock ERC20 tokens ...")
        mock_coins = [
            deploy_mock_erc20(f"Mock Coin{i}", coin.symbol(), coin.decimals(), self.acc)
            for i, coin in enumerate(self._refs["coins"])
        ]

        # deploy the mock lp token and mint existing liquidity tokens
        mock_lp = deploy_mock_lp("Mock Curve V2 LP", "crv3m", self.acc)

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
            mock_coins,
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
            self.acc,
        )

        self._mocks = {
            "coins": mock_coins,
            "lp": mock_lp,
            "pool": mock_pool,
        }
