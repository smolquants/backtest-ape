from typing import ClassVar, List, Mapping

from backtest_ape.gearbox.v2.base import BaseGearboxV2Runner


class GearboxV2STETHRunner(BaseGearboxV2Runner):
    collateral_addrs: ClassVar[List[str]] = [
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",  # stETH
    ]
    _backtester_name = "GearboxV2CABacktest"

    def setup(self, mocking: bool = True):
        """
        Sets up Gearbox V2 stETH strategy runner for testing. Deploys mock
        feeds needed for collateral tokens, if mocking. Then deploys the
        Gearbox V2 CA backtester.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        super().setup(mocking=mocking)

        # deploy the backtester
        manager_addr = self._refs["manager"].address
        self.deploy_strategy(*[manager_addr])
        self._initialized = True

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Overrides BaseGearboxV2Runner::init_mocks_state to setup
        backtester.

        Args:
            state(Mapping): The init state of mocks.
        """
        super().init_mocks_state(state)

        # TODO: deploy backtester with a call to self.backtester.multicall
        # TODO: that creates the stETH strategy through backtester contract
