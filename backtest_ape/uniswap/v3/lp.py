import os
from typing import ClassVar, Mapping, Optional

import pandas as pd
from ape import chain
from hexbytes import HexBytes

from backtest_ape.uniswap.v3.base import BaseUniswapV3Runner
from backtest_ape.utils import get_block_identifier


class UniswapV3LPRunner(BaseUniswapV3Runner):
    tick_lower: int = 0
    tick_upper: int = 0
    amount_weth: int = 0
    amount_token: int = 0
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
        # TODO: Fix for general tokens
        mock_weth = self._mocks["weth"]
        mock_token = self._mocks["token"]
        mock_manager = self._mocks["manager"]
        mock_pool = self._mocks["pool"]
        ecosystem = chain.provider.network.ecosystem

        # set the tick first for position manager add liquidity to work properly
        mock_pool.setTick(state["slot0"].tick, sender=self.acc)

        # mint both tokens to backtester, approve manager to transfer,
        targets = [
            mock_weth.address,
            mock_token.address,
            mock_weth.address,
            mock_token.address,
        ]
        datas = [
            ecosystem.encode_transaction(
                mock_weth.address,
                mock_weth.mint.abis[0],
                self.backtester.address,
                self.amount_weth,
            ).data,
            ecosystem.encode_transaction(
                mock_token.address,
                mock_token.mint.abis[0],
                self.backtester.address,
                self.amount_token,
            ).data,
            ecosystem.encode_transaction(
                mock_weth.address,
                mock_weth.approve.abis[0],
                mock_manager.address,
                2**256 - 1,
            ).data,
            ecosystem.encode_transaction(
                mock_token.address,
                mock_token.approve.abis[0],
                mock_manager.address,
                2**256 - 1,
            ).data,
        ]
        values = [0, 0, 0, 0]
        self.backtester.multicall(targets, datas, values, sender=self.acc)

        # then mint the LP position
        mint_params = (
            mock_weth.address,
            mock_token.address,
            3000,
            self.tick_lower,
            self.tick_upper,
            self.amount_weth,
            self.amount_token,
            0,
            0,
            self.backtester.address,
            chain.blocks.head.timestamp + 86400,
        )
        receipt = self.backtester.execute(
            mock_manager.address,
            ecosystem.encode_transaction(
                mock_manager.address, mock_manager.mint.abis[0], mint_params
            ).data,
            0,
            sender=self.acc,
        )  # TODO: fix
        result = receipt.return_value
        if result == HexBytes("0x"):
            raise ValueError("unexpected result from multicall for token ID")
        token_id = int(bytes(result))  # TODO: check

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
        header = not os.path.exists(path)
        df = pd.DataFrame(
            data={
                "number": number,
                "tick": state["slot0"].tick,
                "liquidity": state["liquidity"],
                "feeGrowthGlobal0X128": state["fee_growth_global0_x128"],
                "feeGrowthGlobal1X128": state["fee_growth_global1_x128"],
                "value": value,
            }
        )
        df.to_csv(path, index=False, mode="a", header=header)
