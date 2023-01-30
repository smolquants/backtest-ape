from ape import accounts, chain
from ape.api.accounts import AccountAPI
from typing import Optional


def get_test_account() -> AccountAPI:
    return accounts.test_accounts[0]


def get_impersonated_account(address: str) -> AccountAPI:
    return accounts[address]


def get_block_identifier(number: Optional[int] = None) -> int:
    return number if number is not None else chain.blocks.head.number
