import pandas as pd

from ape.contracts import ContractInstance
from pydantic import BaseModel
from typing import Mapping, Optional


class BaseRunner(BaseModel):
    _mocks: Mapping[str, ContractInstance] = {}
    _initialized: bool = False

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

        Returns:
            :class:`pandas.DataFrame`: The generated backtester values.
        """
        raise NotImplementedError("forwardtest not implemented.")
