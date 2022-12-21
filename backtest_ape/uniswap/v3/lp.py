import pandas as pd

from ape import chain, project
from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from hexbytes import HexBytes
from typing import Mapping


class UniswapV3LPRunner(BaseUniswapV3Runner):
    tick_lower: int
    tick_upper: int
    amount_tokenA: int
    amount_tokenB: int

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
        mock_tokenA = self._mocks["tokenA"]
        mock_tokenB = self._mocks["tokenB"]
        mock_manager = self._mocks["manager"]
        mock_pool = self._mocks["pool"]
        ecosystem = chain.provider.network.ecosystem

        # set the tick first for position manager add liquidity to work properly
        mock_pool.setTick(state["slot0"].tick, sender=self._acc)

        # mint both tokens to backtester, approve manager to transfer,
        targets = [
            mock_tokenA.address,
            mock_tokenB.address,
            mock_tokenA.address,
            mock_tokenB.address,
        ]
        datas = [
            ecosystem.encode_transaction(
                mock_tokenA.address,
                mock_tokenA.mint.abis[0],
                self._backtester.address,
                self.amount_weth,
            ).data,
            ecosystem.encode_transaction(
                mock_tokenB.address,
                mock_tokenB.mint.abis[0],
                self._backtester.address,
                self.amount_token,
            ).data,
            ecosystem.encode_transaction(
                mock_tokenA.address,
                mock_tokenA.approve.abis[0],
                mock_manager.address,
                2**256 - 1,
            ).data,
            ecosystem.encode_transaction(
                mock_tokenB.address,
                mock_tokenB.approve.abis[0],
                mock_manager.address,
                2**256 - 1,
            ).data,
        ]
        values = [0, 0, 0, 0]
        self._backtester.multicall(targets, datas, values, sender=self._acc)

        # then mint the LP position
        is_a_zero = mock_pool.token0() == mock_tokenA.address
        mock_token0 = mock_tokenA if is_a_zero else mock_tokenB
        mock_token1 = mock_tokenB if is_a_zero else mock_tokenA
        mock_pool_fee = mock_pool.fee()
        amount_token0 = self.amount_tokenA if is_a_zero else self.amount_tokenB
        amount_token1 = self.amount_tokenB if is_a_zero else self.amount_tokenA
        mint_params = (
            mock_token0.address,
            mock_token1.address,
            mock_pool_fee,
            self.tick_lower,
            self.tick_upper,
            amount_token0,
            amount_token1,
            0,
            0,
            self._backtester.address,
            chain.blocks.head.timestamp + 86400,
        )
        receipt = self._backtester.execute(
            mock_manager.address,
            ecosystem.encode_transaction(
                mock_manager.address, mock_manager.mint.abis[0], mint_params
            ).data,
            0,
            sender=self._acc,
        )  # TODO: fix
        result = receipt.return_value
        if result == HexBytes("0x"):
            raise ValueError("unexpected result from multicall for token ID")
        token_id = int(bytes(result))  # TODO: check

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

    def record(
        self, df: pd.DataFrame, number: int, state: Mapping, value: int
    ) -> pd.DataFrame:
        """
        Records the value and possibly some state at the given block.

        Args:
            df (:class:`pd.DataFrame`): The dataframe to record in.
            number (int): The block number.
            state (Mapping): The state of references at block number.
            value (int): The value of the backtester for the state.
        """
        row = pd.DataFrame(
            data={
                "number": number,
                "tick": state["slot0"].tick,
                "liquidity": state["liquidity"],
                "feeGrowthGlobal0X128": state["fee_growth_global0_x128"],
                "feeGrowthGlobal1X128": state["fee_growth_global1_x128"],
                "value": value,
            }
        )
        return pd.concat([df, row])
