from typing import ClassVar

from backtest_ape.uniswap.v3.lp.base import UniswapV3LPBaseRunner


class UniswapV3LPTotalRunner(UniswapV3LPBaseRunner):
    _backtester_name: ClassVar[str] = "UniswapV3LPTotalBacktest"
