import pandas as pd

from ape import chain, project
from backtest_ape.curve.v2.base import BaseCurveV2Runner
from pydantic import validator
from typing import List, Mapping


class CurveV2LPRunner(BaseCurveV2Runner):
    amounts: List[int]

    @validator("amounts")
    def amounts_len_equals_num_coins(cls, v, values, **kwargs):
        if "num_coins" in values and len(v) != values["num_coins"]:
            raise ValueError("len(amounts) != num_coins")
        return v

    def setup(self):
        """
        Sets up Curve V2 LP runner for testing.

        Deploys mock ERC20 tokens needed for pool and mock Curve V2 pool. Then
        deploys the Curve V2 LP backtester.
        """
        super().setup()

        # deploy the backtester
        pool = self._mocks["pool"]
        self._backtester = project.CurveV2LPBacktest.deploy(
            pool.address, self.num_coins, sender=self._acc
        )
        self._initialized = True

    def get_refs_state(self, number: int) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            number (int): The block number to reference.

        Returns:
            Mapping: The state of references at block.
        """
        ref_pool = self._refs["pool"]
        state = {}

        num_coins = self.num_coins
        state["balances"] = [
            ref_pool.balances(i, block_identifier=number) for i in range(num_coins)
        ]
        state["D"] = ref_pool.D(block_identifier=number)
        state["A_gamma"] = [
            ref_pool.initial_A_gamma(block_identifier=number),
            ref_pool.future_A_gamma(block_identifier=number),
            ref_pool.initial_A_gamma_time(block_identifier=number),
            ref_pool.future_A_gamma_time(block_identifier=number),
        ]
        state["prices"] = [
            ref_pool.price_oracle(i, block_identifier=number)
            for i in range(num_coins - 1)
        ]
        return state

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        mock_pool = self._mocks["pool"]
        mock_coins = self._mocks["coins"]
        ecosystem = chain.provider.network.ecosystem

        # set the current balances and D on pool for liquidity add to work
        self.set_mocks_state(state)

        # mint tokens to backtester, approve pool to transfer
        targets = [mock_coin.address for mock_coin in mock_coins]
        datas = [
            ecosystem.encode_transaction(
                mock_coin.address,
                mock_coin.mint.abis[0],
                self._backtester.address,
                self.amounts[i],
            ).data
            for i, mock_coin in enumerate(mock_coins)
        ]
        datas += [
            ecosystem.encode_transaction(
                mock_coin.address,
                mock_coin.approve.abis[0],
                mock_pool.address,
                2**256 - 1,
            ).data
            for i, mock_coin in enumerate(mock_coins)
        ]
        values = [0 for _ in range(2 * self.num_coins)]
        self._backtester.multicall(targets, datas, values, sender=self._acc)

        # then mint the LP position
        self._backtester.execute(
            mock_pool.address,
            ecosystem.encode_transaction(
                mock_pool.address,
                mock_pool.add_liquidity.abis[0],
                self.amounts,
                0,
            ),
            0,
            sender=self._acc,
        )

        # set the mock state again so liquidity changes use ref state
        self.set_mocks_state(state)

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        mock_pool = self._mocks["pool"]
        mock_pool.set_balances(state["balances"], sender=self._acc)
        mock_pool.set_D(state["D"], sender=self._acc)
        mock_pool.set_A_gamma(state["A_gamma"], sender=self._acc)
        mock_pool.set_packed_prices(state["prices"], sender=self._acc)

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

        Returns:
            :class:`pd.DataFrame`: The updated dataframe with the new record.
        """
        row = pd.DataFrame(
            data={
                "number": number,
                "balances": state["balances"],
                "prices": state["prices"],
                "value": value,
            }
        )
        return pd.concat([df, row])
