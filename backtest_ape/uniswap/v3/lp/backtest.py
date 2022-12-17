import click
from ape import accounts

from ..utils import setup


def main():
    """
    Deploys mock Uniswap pool using mock tokens to simulate LP performance
    given a historical (or generated) price path.
    """
    # fake account to use for deployments
    acc = accounts.test_accounts[0]

    # set up mock deployments
    click.echo("Set up mock deployments ...")
    mocks = setup(acc)

    print("mocks", mocks)

    # TODO: mint liquidity
