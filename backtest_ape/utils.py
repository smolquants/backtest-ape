from ape import accounts, chain
from typing import Optional


def get_test_account():
    return accounts.test_accounts[0]


def get_block_identifier(number: Optional[int] = None) -> int:
    return number if number is not None else chain.blocks.head.number
