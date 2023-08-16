from typing import Any, ClassVar, List, Mapping, Optional

import click
import pandas as pd
from ape import Contract, chain, networks, project
from ape.api.accounts import AccountAPI
from ape.api.transactions import TransactionAPI
from ape.contracts import ContractInstance
from ape.exceptions import ContractLogicError
from pydantic import BaseModel, validator

from backtest_ape.utils import fund_account, get_impersonated_account, get_test_account


class BaseRunner(BaseModel):
    ref_addrs: Mapping[str, str] = {}
    acc_addr: Optional[str] = None

    _ref_keys: ClassVar[List[str]] = []
    _refs: Mapping[str, ContractInstance] = {}
    _ref_txs: Mapping[int, List[TransactionAPI]] = {}
    _mocks: Mapping[str, ContractInstance] = {}
    _acc: Optional[AccountAPI] = None
    _initial_acc_balance: int = 0
    _backtester_name: ClassVar[str] = ""
    _backtester: Optional[ContractInstance] = None
    _initialized: bool = False

    @validator("ref_addrs")
    def ref_addrs_has_keys(cls, v):
        if set(cls._ref_keys) > set(v.keys()):
            raise ValueError("cls._ref_keys not subset of ref_addrs.keys()")
        return v

    def __init__(self, **data: Any):
        """
        Overrides BaseModel init to initialize and store the ape Contract
        instances of reference addresses.
        """
        super().__init__(**data)
        self._refs = {k: Contract(ref_addr) for k, ref_addr in self.ref_addrs.items()}

        # set either as impersonated account or test account
        test_acc = get_test_account()
        self._initial_acc_balance = test_acc.balance
        self._acc = (
            get_impersonated_account(self.acc_addr)
            if self.acc_addr is not None
            else test_acc
        )
        self.fund_account()

    class Config:
        underscore_attrs_are_private = True

    @property
    def acc(self):
        if self._acc is None:
            raise Exception("runner account not set.")
        return self._acc

    @property
    def backtester(self):
        if self._backtester is None:
            raise Exception("backtester strategy not deployed.")
        return self._backtester

    def fund_account(self):
        """
        Funds runner account with initial account balance.
        """
        if self._acc.balance < self._initial_acc_balance:
            fund_account(self._acc.address, self._initial_acc_balance)

    def setup(self, mocking: bool = True):
        """
        Sets up the runner for testing.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        raise NotImplementedError("setup not implemented.")

    def get_refs_state(self, number: Optional[int] = None) -> Mapping:
        """
        Gets the state of references at given block.

        Args:
            number (int): The block number. If None, then last block
                from current provider chain.

        Returns:
            Mapping: The state of references at block.
        """
        raise NotImplementedError("get_refs_state not implemented.")

    def deploy_mocks(self):
        """
        Deploys the mock contracts.
        """
        raise NotImplementedError("deploy_mocks not implemented.")

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        raise NotImplementedError("init_mocks_state not implemented.")

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        raise NotImplementedError("set_mocks_state not implemented.")

    def deploy_strategy(self, *args):
        """
        Deploys the backtester strategy contract.
        """
        if self._backtester is not None:
            raise Exception("backtester strategy already deployed.")

        self._backtester = getattr(project, self._backtester_name).deploy(
            *args, sender=self.acc
        )

    def init_strategy(self):
        """
        Initializes the strategy being backtested through backtester contract
        at the given block.
        """
        raise NotImplementedError("init_strategy not implemented.")

    def update_strategy(self, number: int, state: Mapping):
        """
        Updates the strategy being backtested through backtester contract.

        Args:
            number (int): The block number.
            state (Mapping): The state of references at block number.
        """
        raise NotImplementedError("update_strategy not implemented.")

    def record(self, path: str, number: int, state: Mapping, value: int):
        """
        Records the value and possibly some state at the given block.

        Args:
            path (str): The path to the csv file to write the record to.
            number (int): The block number.
            state (Mapping): The state of references at block number.
            value (int): The value of the backtester for the state.
        """
        raise NotImplementedError("record not implemented.")

    def reset_fork(self, number: int):
        """
        Resets the fork state to the given block.

        WARNING: reset_fork with anvil, hardhat providers does *not* seem
        to set the initial base fee to that of number automatically, so this
        method manually sets via RPC call.

        Args:
            number (Optiona[int]): The block number.
        """
        endpoint = None
        if chain.provider.name == "foundry":
            endpoint = "anvil_setNextBlockBaseFeePerGas"
        elif chain.provider.name == "hardhat":
            endpoint = "hardhat_setNextBlockBaseFeePerGas"

        if endpoint is None:
            raise Exception("provider not foundry or hardhat.")

        chain.provider.reset_fork(number)
        base_fee = chain.blocks.head.base_fee
        chain.provider._make_request(endpoint, [base_fee])

    def get_ref_txs(self, number: int) -> List[TransactionAPI]:
        """
        Get reference transactions for the given block.

        Args:
            number (Optional[int]): The block number.
        """
        ecosystem_name = chain.provider.network.ecosystem.name
        upstream_name = chain.provider.config.fork[ecosystem_name][
            "mainnet"
        ].upstream_provider
        with networks.parse_network_choice(
            f"{ecosystem_name}:mainnet:{upstream_name}"
        ) as provider:
            return provider.get_block(block_id=number).transactions

    def submit_tx(self, tx: TransactionAPI):
        """
        Submits a transaction, silently handling reverts.

        Args:
            tx (TransactionAPI): The transaction.
        """
        try:
            tx.required_confirmations = None
            _ = chain.provider.send_transaction(tx)
        except ContractLogicError:
            # let txs that revert fail silently
            # TODO: fix
            pass

    def submit_txs(self, txs: List[TransactionAPI]):
        """
        Submits list of transactions, silently handling reverts.

        Args:
            txs (List): The transactions.
        """
        # TODO: possible to bundle txs into single fork block?
        for tx in txs:
            self.submit_tx(tx)

    def backtest(
        self,
        path: str,
        start: int,
        stop: Optional[int] = None,
        step: Optional[int] = 1,
    ):
        """
        Backtests strategy between start and stop blocks using mocks.

        Args:
            path (str): The path to the csv file to write the record to.
            start (int): The start block number.
            stop (Optional[int]): The stop block number.
            step (Optional[int]): The step interval size.
        """
        if chain.provider.network.name != "mainnet-fork":
            raise Exception("network not mainnet-fork.")

        if stop is None:
            stop = chain.blocks.head.number

        if start > stop:
            raise ValueError("start block after stop block.")

        click.echo("Setting up runner ...")
        self.setup(mocking=True)

        if not self._initialized:
            raise Exception("runner not initialized.")

        click.echo(f"Initializing state of mocks from block number {start} ...")
        self.init_mocks_state(self.get_refs_state(start))

        click.echo(
            f"Iterating from block number {start+1} to {stop} with step size {step} ..."
        )
        for number in range(start + 1, stop, step):
            click.echo(f"Processing block {number} ...")

            # get the state of refs for vars care about at block.number
            refs_state = self.get_refs_state(number)
            click.echo(f"State of refs at block {number}: {refs_state}")

            # set the state of mocks to refs state for vars
            self.set_mocks_state(refs_state)

            # record value function on backtester and any additional state
            value = self.backtester.value()
            click.echo(f"Backtester value at block {number}: {value}")
            self.record(path, number, refs_state, value)

            # update backtested strategy based off new mock state, if needed
            click.echo(f"Updating strategy at block {number} ...")
            self.update_strategy(number, refs_state)

            # replenish funds for acc
            click.echo("Replenishing funds in account ...")
            self.fund_account()

    def replay(
        self,
        path: str,
        start: int,
        stop: Optional[int] = None,
    ):
        """
        Replays strategy against full history of chain between start and
        stop blocks.

        WARNING: Contracts that rely on block.number *won't* replay
        as they would have historically as this function will mine
        a new block for each historical transaction. Further, any
        strategy updates that unintentionally cause reverts for
        txs from the actual chain history will cause the strategy to
        not replay as it would have historically.

        Args:
            path (str): The path to the csv file to write the record to.
            start (int): The start block number.
            stop (Optional[int]): The stop block number.
        """
        if chain.provider.network.name != "mainnet-fork":
            raise Exception("network not mainnet-fork.")

        if stop is None:
            stop = chain.blocks.head.number

        if start > stop:
            raise ValueError("start block after stop block.")

        click.echo(f"Resetting fork to block number {start} ...")
        self.reset_fork(start)

        click.echo("Setting up runner ...")
        self.setup(mocking=False)

        if not self._initialized:
            raise Exception("runner not initialized.")

        click.echo(f"Initializing state of strategy at block number {start} ...")
        self.init_strategy()

        click.echo(
            f"Iterating from block number {start+1} to {stop} with step size 1 ..."
        )
        for number in range(start + 1, stop, 1):
            click.echo(f"Processing block {number} ...")

            # get the state of refs for vars care about at current chain state
            refs_state = self.get_refs_state()
            click.echo(f"State of refs at block {number}: {refs_state}")

            # get the ref network txs at historical block.number and submit to chain
            ref_txs = self.get_ref_txs(number)
            click.echo(f"Submitting {len(ref_txs)} ref txs from block {number} ...")
            self.submit_txs(ref_txs)

            # record value function on backtester
            value = self.backtester.value()
            click.echo(f"Backtester value at block {number}: {value}")
            self.record(path, number, refs_state, value)

            # update backtested strategy based off current chain state, if needed
            click.echo(f"Updating strategy at block {number} ...")
            self.update_strategy(number, refs_state)

            # replenish funds for acc
            click.echo("Replenishing funds in account ...")
            self.fund_account()

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
