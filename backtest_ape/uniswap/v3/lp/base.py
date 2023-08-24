import os
from typing import ClassVar, Mapping, Optional

import pandas as pd

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from backtest_ape.uniswap.v3.lp.mgmt import mint_lp_position
from backtest_ape.uniswap.v3.lp.setup import approve_mock_tokens, mint_mock_tokens
from backtest_ape.utils import get_block_identifier


class UniswapV3LPBaseRunner(BaseUniswapV3Runner):
    tick_lower: int = 0
    tick_upper: int = 0
    amount0: int = 0
    amount1: int = 0
    _backtester_name: ClassVar[str] = "UniswapV3LPBacktest"

    def setup(self, mocking: bool = True):
        """
        Sets up Uniswap V3 LP runner for testing.

        If mocking, deploys mock ERC20 tokens needed for pool, mock Uniswap V3 factory
        and mock Uniswap V3 position manager. Deploys the mock pool
        through the factory.

        Then deploys the Uniswap V3 LP backtester.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        super().setup(mocking=mocking)

        # deploy the backtester
        manager_addr = (
            self._mocks["manager"].address if mocking else self._refs["manager"].address
        )
        self.deploy_strategy(*[manager_addr])
        self._initialized = True

    def get_refs_state(self, number: Optional[int] = None) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            block_number (int): The block number to reference. If None, then
                last block from current provider chain.

        Returns:
            Mapping: The state of references at block.
        """
        block_identifier = get_block_identifier(number)
        ref_pool = self._refs["pool"]
        state = {}

        state["slot0"] = ref_pool.slot0(block_identifier=block_identifier)
        state["liquidity"] = ref_pool.liquidity(block_identifier=block_identifier)
        state["fee_growth_global0_x128"] = ref_pool.feeGrowthGlobal0X128(
            block_identifier=block_identifier
        )
        state["fee_growth_global1_x128"] = ref_pool.feeGrowthGlobal1X128(
            block_identifier=block_identifier
        )
        state["tick_info_lower"] = ref_pool.ticks(
            self.tick_lower, block_identifier=block_identifier
        )
        state["tick_info_upper"] = ref_pool.ticks(
            self.tick_upper, block_identifier=block_identifier
        )
        return state

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        mock_tokens = self._mocks["tokens"]
        mock_manager = self._mocks["manager"]
        mock_pool = self._mocks["pool"]

        # set the tick first for position manager add liquidity to work properly
        mock_pool.setSqrtPriceX96(state["slot0"].sqrtPriceX96, sender=self.acc)

        # approve manager for infinite spend on mock tokens
        approve_mock_tokens(
            mock_tokens,
            self.backtester,
            mock_manager,
            self.acc,
        )

        # mint both tokens to backtester
        mint_mock_tokens(
            mock_tokens,
            self.backtester,
            [self.amount0, self.amount1],
            self.acc,
        )

        # then mint the LP position
        mint_lp_position(
            mock_manager,
            mock_pool,
            self.backtester,
            [self.tick_lower, self.tick_upper],
            [self.amount0, self.amount1],
            self.acc,
        )
        token_id = self.backtester.count() + 1

        # store token id in backtester
        self.backtester.push(token_id, sender=self.acc)

        # set the mock state
        self.set_mocks_state(state)

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        mock_pool = self._mocks["pool"]
        datas = [
            mock_pool.setSqrtPriceX96.as_transaction(state["slot0"].sqrtPriceX96).data,
            mock_pool.setLiquidity.as_transaction(state["liquidity"]).data,
            mock_pool.setFeeGrowthGlobalX128.as_transaction(
                state["fee_growth_global0_x128"], state["fee_growth_global1_x128"]
            ).data,
            mock_pool.setFeeGrowthOutsideX128.as_transaction(
                self.tick_lower,
                state["tick_info_lower"].feeGrowthOutside0X128,
                state["tick_info_lower"].feeGrowthOutside1X128,
            ).data,
            mock_pool.setFeeGrowthOutsideX128.as_transaction(
                self.tick_upper,
                state["tick_info_upper"].feeGrowthOutside0X128,
                state["tick_info_upper"].feeGrowthOutside1X128,
            ).data,
        ]
        mock_pool.calls(datas, sender=self.acc)

    def update_strategy(self, number: int, state: Mapping):
        """
        Updates the strategy being backtested through backtester contract.

        NOTE: Passing means passive LP.

        Args:
            number (int): The block number.
            state (Mapping): The state of references at block number.
        """
        pass

    def record(self, path: str, number: int, state: Mapping, value: int):
        """
        Records the value and possibly some state at the given block.

        Args:
            path (str): The path to the csv file to write the record to.
            number (int): The block number.
            state (Mapping): The state of references at block number.
            value (int): The value of the backtester for the state.
        """
        data = {"number": number, "value": value}
        data.update(
            {
                "sqrtPriceX96": state["slot0"].sqrtPriceX96,
                "liquidity": state["liquidity"],
                "feeGrowthGlobal0X128": state["fee_growth_global0_x128"],
                "feeGrowthGlobal1X128": state["fee_growth_global1_x128"],
                "tickLowerFeeGrowthOutside0X128": state[
                    "tick_info_lower"
                ].feeGrowthOutside0X128,
                "tickLowerFeeGrowthOutside1X128": state[
                    "tick_info_lower"
                ].feeGrowthOutside1X128,
                "tickUpperFeeGrowthOutside0X128": state[
                    "tick_info_upper"
                ].feeGrowthOutside0X128,
                "tickUpperFeeGrowthOutside1X128": state[
                    "tick_info_upper"
                ].feeGrowthOutside1X128,
            }
        )

        header = not os.path.exists(path)
        df = pd.DataFrame(data={k: [v] for k, v in data.items()})
        df.to_csv(path, index=False, mode="a", header=header)
