from typing import List

from ape import chain
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance


def approve_mock_tokens(
    tokens: List[ContractInstance],
    backtester: ContractInstance,
    spender: ContractInstance,
    acc: AccountAPI,
):
    """
    Infinite approves spender contract to spend backtester's
    mock tokens through backtester multicall.
    """
    if len(tokens) != 2:
        raise ValueError("len(tokens) != 2 for approving")

    ecosystem = chain.provider.network.ecosystem
    targets = [
        tokens[0].address,
        tokens[1].address,
    ]
    datas = [
        ecosystem.encode_transaction(
            tokens[0].address,
            tokens[0].approve.abis[0],
            spender.address,
            2**256 - 1,
        ).data,
        ecosystem.encode_transaction(
            tokens[1].address,
            tokens[1].approve.abis[0],
            spender.address,
            2**256 - 1,
        ).data,
    ]
    values = [0, 0]
    backtester.multicall(targets, datas, values, sender=acc)


def mint_mock_tokens(
    tokens: List[ContractInstance],
    backtester: ContractInstance,
    amounts: List[int],
    acc: AccountAPI,
):
    """
    Mints tokens to backtester via backtester multicall.
    """
    if len(tokens) != 2:
        raise ValueError("len(tokens) != 2 for minting")

    ecosystem = chain.provider.network.ecosystem
    targets = [
        tokens[0].address,
        tokens[1].address,
    ]
    datas = [
        ecosystem.encode_transaction(
            tokens[0].address,
            tokens[0].mint.abis[0],
            backtester.address,
            amounts[0],
        ).data,
        ecosystem.encode_transaction(
            tokens[1].address,
            tokens[1].mint.abis[0],
            backtester.address,
            amounts[1],
        ).data,
    ]
    values = [0, 0]
    backtester.multicall(targets, datas, values, sender=acc)
