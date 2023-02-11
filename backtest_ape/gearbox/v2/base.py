from typing import Any, ClassVar, List

import click
from ape import Contract

from backtest_ape.base import BaseRunner
from backtest_ape.gearbox.v2.setup import deploy_mock_feed


class BaseGearboxV2Runner(BaseRunner):
    _ref_keys: ClassVar[List[str]] = ["manager"]

    def __init__(self, **data: Any):
        """
        Overrides BaseRunner init to also store ape Contract instances
        for credit facade, price oracle, supported collateral tokens, and
        feeds associated with each ref token.
        """
        super().__init__(**data)

        # store the facade contract in _refs
        manager = self._refs["manager"]
        self._refs["facade"] = Contract(manager.creditFacade())

        # store price oracle contract in _refs
        price_oracle = Contract(manager.priceOracle())
        self._refs["price_oracle"] = price_oracle

        # store supported collateral contracts in _refs
        tokens = [
            Contract(manager.collateralTokens(i).token)
            for i in range(manager.collateralTokensCount())
        ]
        self._refs["tokens"] = tokens

        # store feeds associated with collateral tokens in _refs
        self._refs["feeds"] = [
            Contract(price_oracle.priceFeeds(token.address)) for token in tokens
        ]

    def setup(self, mocking: bool = True):
        """
        Sets up Gearbox V2 runner for testing. Deploys mock Chainlink
        oracles, if mocking.

        Args:
            mocking (bool): Whether to deploy mocks.
        """
        if mocking:
            self.deploy_mocks()

    def deploy_mocks(self):
        """
        Deploys the mock contracts.
        """
        # deploy the mock Chainlink feed
        click.echo("Deploying mock feeds ...")
        mock_feeds = [
            deploy_mock_feed(
                feed.description(),
                feed.decimals(),
                feed.version(),
                self.acc,
            )
            for i, feed in enumerate(self._refs["feeds"])
        ]
        self._mocks = {"feeds": mock_feeds}
