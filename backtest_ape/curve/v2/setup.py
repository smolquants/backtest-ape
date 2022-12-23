from ape import project
from ape.contracts import ContractInstance
from ape.api.accounts import AccountAPI
from typing import List


def deploy_mock_pool(
    coins: List[ContractInstance],
    A: int,
    gamma: int,
    mid_fee: int,
    out_fee: int,
    allowed_extra_profit: int,
    fee_gamma: int,
    adjustment_step: int,
    admin_fee: int,
    ma_half_time: int,
    prices: List[int],
    acc: AccountAPI,
) -> ContractInstance:
    """
    Deploys mock Curve V2 pool.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    params = (
        acc.address,
        acc.address,
        A,
        gamma,
        mid_fee,
        out_fee,
        allowed_extra_profit,
        fee_gamma,
        adjustment_step,
        admin_fee,
        ma_half_time,
        prices,
    )
    pool = project.MockTricrypto2.deploy(*params, sender=acc)
    return pool
