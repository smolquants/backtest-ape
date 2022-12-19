from ape import project
from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from typing import Mapping


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

    def get_refs_state(self, number: int) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            block_number (int): The block number to reference.

        Returns:
            Mapping: The state of references at block.
        """
        ref_pool = self._refs["pool"]
        state = {}

        state["slot0"] = ref_pool.slot0(block_identifier=number)
        state["liquidity"] = ref_pool.liquidity(block_identifier=number)
        state["fee_growth_global0_x128"] = ref_pool.feeGrowthGlobal0X128(
            block_identifier=number
        )
        state["fee_growth_global1_x128"] = ref_pool.feeGrowthGlobal1X128(
            block_identifier=number
        )
        state["tick_info_lower"] = ref_pool.ticks(
            self.tick_lower, block_identifier=number
        )
        state["tick_info_upper"] = ref_pool.ticks(
            self.tick_upper, block_identifier=number
        )

        return state

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        mock_pool = self._mocks["pool"]
        datas = [
            mock_pool.setTick.as_transaction(state["slot0"].tick).data,
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
        mock_pool.calls(datas)
