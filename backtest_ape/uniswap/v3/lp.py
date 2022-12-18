import click
import pandas as pd

from ape import chain, project
from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from typing import Optional


class UniswapV3LPRunner(BaseUniswapV3Runner):
    tick_lower: int
    tick_upper: int
    amount: int

    def setup(self):
        """
        Sets up Uniswap V3 LP runner for testing.

        Deploys mock ERC20 tokens needed for pool, mock Uniswap V3 factory
        and mock Uniswap V3 position manager. Deploys the mock pool
        through the factory.

        Then deploys the Uniswap V3 LP backtester.
        """
        super().setup()

        # deploy the backtester
        manager = self._mocks["manager"]
        self._backtester = project.UniswapV3LPBacktest.deploy(
            manager.address, sender=self._acc
        )

        # TODO: mint both tokens to acc, approve manager to transfer,
        # TODO: then mint LP position

        self._initialized = True

    def backtest(
        self,
        start: int,
        stop: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Backtests Uniswap V3 LP strategy between start and stop blocks.

        Args:
            start (int): The start block number.
            stop (Optional[int]): Then stop block number.

        Returns:
            :class:`pandas.DataFrame`: The generated backtester values.
        """
        if not self._initialized:
            raise Exception("runner not setup.")

        if stop is None:
            stop = chain.blocks.head.number

        if start > stop:
            raise ValueError("start block after stop block.")

        click.echo(f"Iterating from block number {start} to {stop} ...")
        for number in range(start, stop, 1):
            continue

        # TODO: implement
        return pd.DataFrame()

    def forwardtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Forwardtests strategy against Monte Carlo simulated data.

        Args:
            data (:class:`pd.DataFrame`):
                Historical data to generate Monte Carlo sims from.

        Returns:
            :class:`pandas.DataFrame`: The generated backtester values.
        """
        if not self._initialized:
            raise Exception("runner not setup.")

        # TODO: implement
        return pd.DataFrame()
