import os
from typing import Any, ClassVar, List, Mapping, Optional

import pandas as pd
from ape import chain
from pydantic import validator

from backtest_ape.curve.v2.base import BaseCurveV2Runner
from backtest_ape.utils import get_block_identifier


class CurveV2LPRunner(BaseCurveV2Runner):
    amounts: List[int] = []
    _backtester_name: ClassVar[str] = "CurveV2LPBacktest"

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

    def setup(self, mocking: bool = True):
        """
        Sets up Curve V2 LP runner for testing. Deploys mock ERC20 tokens needed
        for pool and mock Curve V2 pool, if mocking. Then deploys the Curve V2
        LP backtester.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        super().setup(mocking=mocking)

        # deploy the backtester
        pool_addr = (
            self._mocks["pool"].address if mocking else self._refs["pool"].address
        )
        self.deploy_strategy(*[pool_addr, self.num_coins])
        self._initialized = True

    def get_refs_state(self, number: Optional[int] = None) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            number (int): The block number. If None, then last block
                from current provider chain.

        Returns:
            Mapping: The state of references at block.
        """
        block_identifier = get_block_identifier(number)
        ref_pool = self._refs["pool"]
        ref_lp = self._refs["lp"]
        state = {}

        num_coins = self.num_coins
        state["balances"] = [
            ref_pool.balances(i, block_identifier=block_identifier)
            for i in range(num_coins)
        ]
        state["D"] = ref_pool.D(block_identifier=block_identifier)
        state["A_gamma"] = [
            ref_pool.initial_A_gamma(block_identifier=block_identifier),
            ref_pool.future_A_gamma(block_identifier=block_identifier),
            ref_pool.initial_A_gamma_time(block_identifier=block_identifier),
            ref_pool.future_A_gamma_time(block_identifier=block_identifier),
        ]
        state["prices"] = [
            ref_pool.price_oracle(i, block_identifier=block_identifier)
            for i in range(num_coins - 1)
        ]
        state["total_supply"] = ref_lp.totalSupply(block_identifier=block_identifier)
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
                self.backtester.address,
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
        self.backtester.multicall(targets, datas, values, sender=self.acc)

        # then mint the LP position
        self.backtester.execute(
            mock_pool.address,
            ecosystem.encode_transaction(
                mock_pool.address,
                mock_pool.add_liquidity.abis[0],
                self.amounts,
                0,
            ).data,
            0,
            sender=self.acc,
        )

        # burn the equivalent amount of minted LP tokens from runner acc
        minted = mock_lp.balanceOf(self.backtester.address)
        mock_lp.burnFrom(self.acc.address, minted, sender=self.acc)

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
        mock_pool.set_balances(state["balances"], sender=self.acc)
        mock_pool.set_D(state["D"], sender=self.acc)
        mock_pool.set_A_gamma(state["A_gamma"], sender=self.acc)
        mock_pool.set_packed_prices(state["prices"], sender=self.acc)

        # update mock LP token supply for state attrs
        mock_lp = self._mocks["lp"]
        d_supply = state["total_supply"] - mock_lp.totalSupply()
        if d_supply >= 0:
            mock_lp.mint(self.acc.address, abs(d_supply), sender=self.acc)
        else:
            mock_lp.burnFrom(self.acc.address, abs(d_supply), sender=self.acc)

    def init_strategy(self):
        """
        Initializes the strategy being backtested through backtester contract
        at the given block.
        """
        pool = self._refs["pool"]
        coins = self._refs["coins"]
        ecosystem = chain.provider.network.ecosystem

        # transfer tokens from acc to backtester
        targets = [coin.address for coin in coins]
        datas = [
            ecosystem.encode_transaction(
                coin.address,
                coin.transfer.abis[0],
                self.backtester.address,
                self.amounts[i],
            ).data
            for i, coin in enumerate(coins)
        ]
        values = [0 for _ in range(self.num_coins)]

        # approve pool to spend each coin
        targets += [coin.address for coin in coins]
        datas += [
            ecosystem.encode_transaction(
                coin.address,
                coin.approve.abis[0],
                pool.address,
                2**256 - 1,
            ).data
            for i, coin in enumerate(coins)
        ]
        values += [0 for _ in range(self.num_coins)]

        # deposit coins to pool as lp
        targets += [pool.address]
        datas += [
            ecosystem.encode_transaction(
                pool.address,
                pool.add_liquidity.abis[0],
                self.amounts,
                0,
            ).data,
        ]
        values += [0]

        # execute through backtester
        self.backtester.multicall(targets, datas, values, sender=self.acc)

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
