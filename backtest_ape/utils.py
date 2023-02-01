from ape import accounts, chain
from ape.api.accounts import AccountAPI
from typing import Optional


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


def fund_account_from(recipient: AccountAPI, sender: AccountAPI):
    """
    Funds an account from the entire balance of another account.

    Args:
        recipient (AccountAPI): The recipient of funds.
        sender (AccountAPI): The sender of funds.
    """
    sender.transfer(recipient, send_everything=True)


def get_block_identifier(number: Optional[int] = None) -> int:
    """
    Gets the block identifier for the given integer number.

    Args:
        number (Optional[int]): The block number. If None, defaults
            to latest block of current provider chain.
    """
    return number if number is not None else chain.blocks.head.number
