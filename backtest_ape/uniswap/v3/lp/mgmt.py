from typing import List

from ape import chain
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance


def mint_lp_position(
    manager: ContractInstance,
    pool: ContractInstance,
    backtester: ContractInstance,
    ticks: List[int],
    amounts: List[int],
    acc: AccountAPI,
):
    """
    Mints a new LP position to backtester.
    """
    if len(ticks) != 2:
        raise ValueError("len(ticks) != 2 for minting lp")
    elif len(amounts) != 2:
        raise ValueError("len(amounts) != 2 for minting lp")

    ecosystem = chain.provider.network.ecosystem
    target = manager.address
    params = (
        pool.token0(),
        pool.token1(),
        pool.fee(),
        ticks[0],  # tick_lower
        ticks[1],  # tick_upper
        amounts[0],  # amount0
        amounts[1],  # amount1
        0,
        0,
        backtester.address,
        chain.blocks.head.timestamp + 86400,
    )
    data = ecosystem.encode_transaction(
        manager.address, manager.mint.abis[0], params
    ).data
    value = 0
    backtester.execute(target, data, value, sender=acc)


def remove_liquidity_from_lp_position(
    manager: ContractInstance,
    pool: ContractInstance,
    backtester: ContractInstance,
    token_id: int,
    liquidity: int,
    acc: AccountAPI,
):
    """
    Removes liquidity from an existing LP position owned by backtester.
    """
    ecosystem = chain.provider.network.ecosystem
    target = manager.address
    params = (token_id, liquidity, 0, 0, chain.blocks.head.timestamp + 86400)
    data = ecosystem.encode_transaction(
        manager.address, manager.decreaseLiquidity.abis[0], params
    ).data
    value = 0
    backtester.execute(target, data, value, sender=acc)
