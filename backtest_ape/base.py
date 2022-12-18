import pandas as pd

from ape import Contract
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
        # TODO: test
        super().__init__(**data)
        self._refs = {k: Contract(ref_addr) for k, ref_addr in self.ref_addrs}

    class Config:
        underscore_attrs_are_private = True

    def setup(self):
        """
        Sets up the runner for testing.
        """
        raise NotImplementedError("setup not implemented.")

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
        raise NotImplementedError("backtest not implemented.")

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
