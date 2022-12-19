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
        values = []
        for number in range(start, stop, 1):
            click.echo(f"Processing block {number} ...")

            # get the state of ref pool for vars care about at block.number
            ref_pool = self._refs["pool"]
            slot0 = ref_pool.slot0(block_identifier=number)
            liquidity = ref_pool.liquidity(block_identifier=number)
            fee_growth_global0_x128 = ref_pool.feeGrowthGlobal0X128(block_identifier=number)
            fee_growth_global1_x128 = ref_pool.feeGrowthGlobal1X128(block_identifier=number)
            tick_info_lower = ref_pool.ticks(self.tick_lower)
            tick_info_upper = ref_pool.ticks(self.tick_upper)

            # set the mock state to ref pool state for vars
            mock_pool = self._mocks["pool"]
            datas = [
                mock_pool.setTick.as_transaction(slot0.tick).data,
                mock_pool.setLiquidity.as_transaction(liquidity).data,
                mock_pool.setFeeGrowthGlobalX128.as_transaction(
                    fee_growth_global0_x128,
                    fee_growth_global1_x128
                ).data,
                mock_pool.setFeeGrowthOutsideX128.as_transaction(
                    self.tick_lower,
                    tick_info_lower.feeGrowthOutside0X128,
                    tick_info_lower.feeGrowthOutside1X128
                ).data,
                mock_pool.setFeeGrowthOutsideX128.as_transaction(
                    self.tick_upper,
                    tick_info_upper.feeGrowthOutside0X128,
                    tick_info_upper.feeGrowthOutside1X128
                ).data,
            ]
            mock_pool.calls(datas)

            # record value function on backtester
            value = self._backtester.value()
            values.append(value)

        return pd.DataFrame(data={
            "number": [number for number in range(start, stop, 1)],
            "value": values
        })

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
