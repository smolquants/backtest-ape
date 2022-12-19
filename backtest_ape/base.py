import click
import pandas as pd

from ape import Contract, chain
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI
from pydantic import BaseModel
from typing import Any, Mapping, Optional


class BaseRunner(BaseModel):
    ref_addrs: Optional[Mapping[str, str]] = {}

    _refs: Mapping[str, ContractInstance]
    _mocks: Mapping[str, ContractInstance]
    _acc: AccountAPI
    _backtester: ContractInstance
    _initialized: bool = False

    def __init__(self, **data: Any):
        """
        Overrides BaseModel init to initialize and store the ape Contract
        instances of reference addresses.
        """
        super().__init__(**data)
        self._refs = {k: Contract(ref_addr) for k, ref_addr in self.ref_addrs.items()}

    class Config:
        underscore_attrs_are_private = True

    def setup(self):
        """
        Sets up the runner for testing.
        """
        raise NotImplementedError("setup not implemented.")

    def get_refs_state(self, number: int) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            number (int): The block number to reference.

        Returns:
            Mapping: The state of references at block.
        """
        raise NotImplementedError("get_refs_state not implemented.")

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        raise NotImplementedError("set_mocks_state not implemented.")

    def update_strategy(self):
        """
        Updates the strategy being backtested through backtester contract.
        """
        raise NotImplementedError("update_strategy not implemented.")

    def backtest(
        self,
        start: int,
        stop: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Backtests strategy between start and stop blocks.

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

            # get the state of refs for vars care about at block.number
            refs_state = self.get_refs_state(number)
            click.echo(f"State of refs at block {number}: {refs_state}")

            # set the state of mocks to refs state for vars
            self.set_mocks_state(refs_state)

            # update backtested strategy based off new mock state, if needed
            self.update_strategy()

            # record value function on backtester
            value = self._backtester.value()
            values.append(value)
            click.echo(f"Backtester value at block {number}: {value}")

        return pd.DataFrame(
            data={
                "number": [number for number in range(start, stop, 1)],
                "value": values,
            }
        )

    def forwardtest(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Forwardtests strategy against Monte Carlo simulated data.

        Args:
            data (:class:`pd.DataFrame`):
                Historical data to generate Monte Carlo sims from.

        Returns:
            :class:`pandas.DataFrame`: The generated backtester values.
        """
        raise NotImplementedError("forwardtest not implemented.")
