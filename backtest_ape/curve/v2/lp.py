import pandas as pd

from ape import chain, project
from backtest_ape.curve.v2.base import BaseCurveV2Runner
from typing import List, Mapping


class CurveV2LPRunner(BaseCurveV2Runner):
    amounts: List[int]

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
            pool.address, 3, sender=self._acc
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

        num_coins = self._backtester.numCoins()
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
        mock_usd = self._mocks["usd"]
        mock_token = self._mocks["token"]
        mock_weth = self._mocks["weth"]
        ecosystem = chain.provider.network.ecosystem

        # set the current balances and D on pool for liquidity add to work
        self.set_mocks_state(state)

        # mint tokens to backtester, approve pool to transfer
        [amount_usd, amount_token, amount_weth] = self.amounts
        targets = [
            mock_usd.address,
            mock_token.address,
            mock_weth.address,
            mock_usd.address,
            mock_token.address,
            mock_weth.address,
        ]
        datas = [
            ecosystem.encode_transaction(
                mock_usd.address,
                mock_usd.mint.abis[0],
                self._backtester.address,
                amount_usd,
            ).data,
            ecosystem.encode_transaction(
                mock_token.address,
                mock_token.mint.abis[0],
                self._backtester.address,
                amount_token,
            ).data,
            ecosystem.encode_transaction(
                mock_weth.address,
                mock_weth.mint.abis[0],
                self._backtester.address,
                amount_weth,
            ).data,
            ecosystem.encode_transaction(
                mock_usd.address,
                mock_usd.approve.abis[0],
                mock_pool.address,
                2**256 - 1,
            ).data,
            ecosystem.encode_transaction(
                mock_token.address,
                mock_token.approve.abis[0],
                mock_pool.address,
                2**256 - 1,
            ).data,
            ecosystem.encode_transaction(
                mock_weth.address,
                mock_weth.approve.abis[0],
                mock_pool.address,
                2**256 - 1,
            ).data,
        ]
        values = [0, 0, 0, 0, 0, 0]
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
