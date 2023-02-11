from enum import Enum
from typing import Any, ClassVar, List, Mapping, Optional, Tuple

import click
from ape import Contract, accounts, chain
from ape.contracts import ContractInstance

from backtest_ape.base import BaseRunner
from backtest_ape.gearbox.v2.setup import deploy_mock_feed
from backtest_ape.utils import get_block_identifier


class PriceFeedType(Enum):
    CHAINLINK_ORACLE = 0
    YEARN_ORACLE = 1
    CURVE_2LP_ORACLE = 2
    CURVE_3LP_ORACLE = 3
    CURVE_4LP_ORACLE = 4
    ZERO_ORACLE = 5
    WSTETH_ORACLE = 6
    BOUNDED_ORACLE = 7
    COMPOSITE_ETH_ORACLE = 8


class BaseGearboxV2Runner(BaseRunner):
    collateral_addrs: ClassVar[List[str]] = []
    supported_feed_types: ClassVar[List[int]] = [
        PriceFeedType.CHAINLINK_ORACLE.value,
        PriceFeedType.COMPOSITE_ETH_ORACLE.value,
    ]
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
        oracles, if mocking, and sets mocks as feeds on price oracle
        for specified collateral addresses.

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

    def _get_feed_data(self, feed: ContractInstance, number: int) -> Tuple:
        """
        Gets reference feed data to be set in associated mock. Transforms
        the fetched data from reference feeds if needed to consolidate
        Gearbox oracle types into Chainlink only X/USD oracle.

        Args:
            feed (:class:`ape.contracts.ContractInstance`): The reference feed.
            number (int): The reference block number.

        Returns:
            Tuple: The Chainlink round data.
        """
        price_feed_type = feed.priceFeedType()
        if price_feed_type not in self.supported_feed_types:
            raise ValueError(f"feed {feed.address} not supported type")

        data = tuple()
        if price_feed_type == PriceFeedType.CHAINLINK_ORACLE.value:
            data = tuple(feed.lastRoundData(block_identifier=number))
        elif price_feed_type == PriceFeedType.COMPOSITE_ETH_ORACLE.value:
            # query the underlying eth/usd and x/eth feeds at number
            feed_eth_usd = Contract(feed.ethUsdPriceFeed())
            feed_target = Contract(feed.targetEthPriceFeed())
            answer_denom = feed.answerDenominator()

            # return target relative to USD at number
            round_data = feed_target.latestRoundData(block_identifier=number)
            round_data_eth_usd = feed_eth_usd.latestRoundData(block_identifier=number)
            round_data.answer = int(
                round_data.answer * round_data_eth_usd.answer / answer_denom
            )

            data = tuple(round_data)

        return data

    def get_refs_state(self, number: Optional[int] = None) -> Mapping:
        """
        Get the state of references at given block.

        Args:
            number (int): The block number. If None, then last block
                from current provider chain.

        Returns:
            Mapping: The state of references at block.
        """
        # only get ref state for collateral addrs care about
        block_identifier = get_block_identifier(number)
        feeds = self._refs["feeds"]
        tokens = self._refs["tokens"]

        state = {
            self._get_feed_data(feed, block_identifier)
            for i, feed in enumerate(feeds)
            if tokens[i].address in self.collateral_addrs
        }
        return state

    def init_mocks_state(self, state: Mapping):
        """
        Initializes the state of mocks.

        Args:
            state (Mapping): The init state of mocks.
        """
        price_oracle = self._refs["price_oracle"]
        acl = Contract(price_oracle._acl())
        configurator = accounts[acl.owner()]  # impersonate configurator

        # set the latest round data and round ID on the mock feeds
        self.set_mocks_state(state)

        # sets mocks as price feeds in ref price oracle contract
        token_addrs = [token.address for token in self._refs["tokens"]]
        for collateral_addr in self.collateral_addrs:
            i = token_addrs.index(collateral_addr)  # get the index in ref
            mock_feed = self._mocks["feeds"][i]
            price_oracle.addPriceFeed(
                collateral_addr, mock_feed.address, sender=configurator
            )

    def set_mocks_state(self, state: Mapping):
        """
        Sets the state of mocks.

        Args:
            state (Mapping): The new state of mocks.
        """
        mock_feeds = self._mocks["feeds"]
        ecosystem = chain.provider.network.ecosystem

        for i, mock_feed in enumerate(mock_feeds):
            round_data = state["feeds"][i]  # round data tuple
            round_id = round_data[0]

            # stores latest round data and sets latest round id
            datas = [
                ecosystem.encode_transaction(
                    mock_feed.address,
                    mock_feed.setRound.abis[0],
                    round_data,
                ).data,
                ecosystem.encode_transaction(
                    mock_feed.address,
                    mock_feed.setLatestRoundId.abis[0],
                    round_id,
                ).data,
            ]
            mock_feed.calls(datas, sender=self.acc)
