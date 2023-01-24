import os
from typing import Any, List, Mapping

import pandas as pd
from ape import chain, project
from pydantic import validator

from backtest_ape.curve.v2.base import BaseCurveV2Runner


class CurveV2LPRunner(BaseCurveV2Runner):
    amounts: List[int]

    @validator("amounts")
    def amounts_len_equals_num_coins(cls, v, values, **kwargs):
        if "num_coins" in values and len(v) != values["num_coins"]:
            raise ValueError("len(amounts) != num_coins")
        return v

    def __init__(self, **data: Any):
        """
        Overrides BaseCurveV2Runner init to also check amounts < balances
        in pool.
        """
        super().__init__(**data)

        # check balances in pool > amounts
        pool = self._refs["pool"]
        for i, coin in enumerate(self._refs["coins"]):
            balance = coin.balanceOf(pool.address)
            if balance < self.amounts[i]:
                raise ValueError("amounts not less than balances")

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
        ref_lp = self._refs["lp"]
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
        state["total_supply"] = ref_lp.totalSupply(block_identifier=number)
        return state

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        mock_pool = self._mocks["pool"]
        mock_lp = self._mocks["lp"]
        mock_coins = self._mocks["coins"]
        ecosystem = chain.provider.network.ecosystem

        # set the current balances and D on pool for liquidity add to work
        self.set_mocks_state(state)

        # mint tokens to backtester, approve pool to transfer
        targets = [mock_coin.address for mock_coin in mock_coins]
        targets += targets
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
            ).data,
            0,
            sender=self._acc,
        )

        # burn the equivalent amount of minted LP tokens from runner acc
        minted = mock_lp.balanceOf(self._backtester.address)
        mock_lp.burnFrom(self._acc.address, minted, sender=self._acc)

        # set the mock state again so liquidity changes use ref state
        self.set_mocks_state(state)

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        # update mock pool for state attrs
        mock_pool = self._mocks["pool"]
        mock_pool.set_balances(state["balances"], sender=self._acc)
        mock_pool.set_D(state["D"], sender=self._acc)
        mock_pool.set_A_gamma(state["A_gamma"], sender=self._acc)
        mock_pool.set_packed_prices(state["prices"], sender=self._acc)

        # update mock LP token supply for state attrs
        mock_lp = self._mocks["lp"]
        d_supply = state["total_supply"] - mock_lp.totalSupply()
        if d_supply >= 0:
            mock_lp.mint(self._acc.address, abs(d_supply), sender=self._acc)
        else:
            mock_lp.burnFrom(self._acc.address, abs(d_supply), sender=self._acc)

    def update_strategy(self):
        """
        Updates the strategy being backtested through backtester contract.

        NOTE: Passing means passive LP.
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
        data.update(state)

        # unfold the lists
        updates = {}
        removes = []
        for k, v in data.items():
            if isinstance(v, list):
                for i, item in enumerate(v):
                    updates[f"{k}{i}"] = item
                removes.append(k)

        # remove the list keys
        for k in removes:
            del data[k]

        # update data for unfolded list items
        data.update(updates)

        # append row to csv file
        header = not os.path.exists(path)
        df = pd.DataFrame(data={k: [v] for k, v in data.items()})
        df.to_csv(path, index=False, mode="a", header=header)
