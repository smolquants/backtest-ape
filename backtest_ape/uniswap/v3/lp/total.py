from typing import ClassVar

from backtest_ape.uniswap.v3.lp.base import UniswapV3LPBaseRunner


class UniswapV3LPTotal0Runner(UniswapV3LPBaseRunner):
    _backtester_name: ClassVar[str] = "UniswapV3LPTotal0Backtest"


class UniswapV3LPTotal1Runner(UniswapV3LPBaseRunner):
    _backtester_name: ClassVar[str] = "UniswapV3LPTotal1Backtest"
