from typing import Any, ClassVar, List, Mapping

from ape import chain
from ape.utils import ZERO_ADDRESS

from backtest_ape.gearbox.v2.base import BaseGearboxV2Runner


class GearboxV2STETHRunner(BaseGearboxV2Runner):
    collateral_amount: int
    leverage_factor: int
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
        manager = self._refs["manager"]
        facade = self._refs["facade"]
        adapter = self._refs["adapter"]
        collateral = self._refs["collaterals"][0]

        # approve WETH for manager to spend, create credit account,
        # then use credit account to enter stETH strategy
        targets = [collateral.address, facade.address, adapter.address]
        datas = [
            ecosystem.encode_transaction(
                collateral.address,
                collateral.approve.abis[0],
                manager.address,
                2**256 - 1,
            ).data,
            ecosystem.encode_transaction(
                facade.address,
                facade.openCreditAccount.abis[0],
                self.collateral_amount,
                self.backtester.address,
                self.leverage_factor,
                0,
            ).data,
            ecosystem.encode_transaction(
                adapter.address,
                adapter.submitAll.abis[0],
            ).data,
        ]
        values = [0, self.collateral_amount, 0]
        self.backtester.multicall(
            targets, datas, values, sender=self.acc, value=self.collateral_amount
        )
