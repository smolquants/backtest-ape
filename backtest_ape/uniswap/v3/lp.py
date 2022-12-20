from ape import chain, project
from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from typing import Mapping


class UniswapV3LPRunner(BaseUniswapV3Runner):
    tick_lower: int
    tick_upper: int
    amount_weth: int
    amount_token: int

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

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        mock_weth = self._mocks["weth"]
        mock_token = self._mocks["token"]
        mock_manager = self._mocks["manager"]
        mock_pool = self._mocks["pool"]

        # set the tick first for position manager add liquidity to work properly
        mock_pool.setTick(state["slot0"].tick)

        # mint both tokens to backtester, approve manager to transfer,
        # then mint LP position
        mint_params = {
            "token0": mock_weth.address,
            "token1": mock_token.address,
            "fee": 3000,
            "tickLower": self.tick_lower,
            "tickUpper": self.tick_upper,
            "amount0Desired": self.amount_weth,
            "amount1Desired": self.amount_token,
            "amount0Min": 0,
            "amount1Min": 0,
            "recipient": self._backtester.address,
            "deadline": chain.blocks.head.timestamp + 86400,
        }
        targets = [
            mock_weth.address,
            mock_token.address,
            mock_weth.address,
            mock_token.address,
            mock_manager.address,
        ]
        datas = [
            mock_weth.mint.as_transaction(
                self._backtester.address, self.amount_weth
            ).data,
            mock_token.mint.as_transaction(
                self._backtester.address, self.amount_token
            ).data,
            mock_weth.approve.as_transaction(
                mock_manager.address, self.amount_weth
            ).data,
            mock_token.approve.as_transaction(
                mock_manager.address, self.amount_token
            ).data,
            mock_manager.mint.as_transaction(mint_params).data,
        ]
        values = [0, 0, 0, 0, 0]
        receipt = self._backtester.multicall(targets, datas, values, sender=self._acc)
        token_id = int(receipt.return_value[-1])  # TODO: check

        # store token id in backtester
        self._backtester.push(token_id, sender=self._acc)

        # set the mock state
        self.set_mock_state(state)

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

    def update_strategy(self):
        """
        Updates the strategy being backtested through backtester contract.

        NOTE: Passing means passive LP.
        """
        pass
