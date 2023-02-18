from typing import Optional

from ape import accounts, chain
from ape.api.accounts import AccountAPI


def get_test_account() -> AccountAPI:
    """
    Gets a test account.
    """
    return accounts.test_accounts[0]


def get_impersonated_account(address: str) -> AccountAPI:
    """
    Gets an impersonated account at the given address.

    Args:
        address (str): The address of the account.
    """
    return accounts[address]


def fund_account(address: str, amount: int):
    """
    Funds an account from the entire balance of another account.

    Args:
        address (str): The recipient of funds.
        amount (int): The funding amount.
    """
    chain.set_balance(address, amount)


def get_block_identifier(number: Optional[int] = None) -> int:
    """
    Gets the block identifier for the given integer number.

    Args:
        number (Optional[int]): The block number. If None, defaults
            to latest block of current provider chain.
    """
    return number if number is not None else chain.blocks.head.number
