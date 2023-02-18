from typing import Any, ClassVar, List, Mapping

from ape import chain
from ape.utils import ZERO_ADDRESS

from backtest_ape.gearbox.v2.base import BaseGearboxV2Runner


class GearboxV2STETHRunner(BaseGearboxV2Runner):
    collateral_amount: int
    borrow_amount: int
    collateral_addrs: ClassVar[List[str]] = [
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",  # stETH
    ]

    _backtester_name: ClassVar[str] = "GearboxV2CABacktest"
    _ref_keys: ClassVar[List[str]] = ["manager", "adapter"]

    def __init__(self, **data: Any):
        """
        Overrides BaseGearboxV2Runner init to also store ape Contract instances
        for collaterals and Lido adapter.
        """
        super().__init__(**data)

        # check adapter supported by credit manager
        manager = self._refs["manager"]
        adapter = self._refs["adapter"]
        if manager.adapterToContract(adapter.address) == ZERO_ADDRESS:
            raise ValueError("adapter not supported by manager")

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

        ecosystem = chain.provider.network.ecosystem
        facade = self._refs["facade"]
        adapter = self._refs["adapter"]

        # create the stETH strategy through backtester contract
        target = facade.address
        calls = [
            (
                adapter.address,
                ecosystem.encode_transaction(
                    adapter.address,
                    adapter.submit.abis[0],
                    self.collateral_amount + self.borrow_amount,
                ).data,
            )
        ]
        data = ecosystem.encode_transaction(
            facade.address,
            facade.openCreditAccountMulticall.abis[0],
            self.borrow_amount,
            self.backtester.address,
            calls,
            0,
        ).data
        val = self.collateral_amount
        self.backtester.execute(target, data, val, sender=self.acc, value=val)
