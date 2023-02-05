from typing import List

from ape import project
from ape.api.accounts import AccountAPI
from ape.contracts import ContractInstance


def deploy_mock_lp(name: str, symbol: str, acc: AccountAPI) -> ContractInstance:
    """
    Deploys mock Curve LP Token.

    Returns:
        :class:`ape.contracts.ContractInstance`
    """
    return project.MockCurveToken.deploy(name, symbol, sender=acc)


def deploy_mock_pool(
    coins: List[ContractInstance],
    lp: ContractInstance,
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
        [coin.address for coin in coins],
        lp.address,
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
