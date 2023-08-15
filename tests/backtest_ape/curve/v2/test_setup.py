from ape.contracts import ContractInstance

from backtest_ape.curve.v2.setup import deploy_mock_lp, deploy_mock_pool
from backtest_ape.setup import deploy_mock_erc20


def test_deploy_mock_lp(acc):
    tok = deploy_mock_lp("Mock Curve Token", "crv3m", acc)
    assert isinstance(tok, ContractInstance) is True
    assert tok.name() == "Mock Curve Token"
    assert tok.symbol() == "crv3m"

    # try minting
    receipt = tok.mint(acc.address, 1000, sender=acc)
    assert receipt.return_value is True
    assert tok.balanceOf(acc) == 1000

    # try relative minting
    frac = 10000000000000000  # 1e16 == 1% of supply
    receipt = tok.mint_relative(acc.address, frac, sender=acc)
    assert receipt.return_value == 10
    assert tok.balanceOf(acc) == 1010

    # try burning
    receipt = tok.burnFrom(acc.address, 100, sender=acc)
    assert receipt.return_value is True
    assert tok.balanceOf(acc) == 910


def test_deploy_mock_pool(acc):
    coins = [deploy_mock_erc20(f"Mock {i}", f"MOK{i}", 18, acc) for i in range(3)]
    lp = deploy_mock_lp("Mock Curve", "crv3m", acc)

    A = 1000000  # 10**6
    gamma = 10000000000000  # 10**13
    mid_fee = 5000000  # 5 bps
    out_fee = 30000000  # 3 bps
    allowed_extra_profit = 2000000000000  # 2 * 10**12
    fee_gamma = 500000000000000
    adjustment_step = 2000000000000000
    admin_fee = 5000000000
    ma_half_time = 600
    price = 1000000000000000000  # 1 wad
    pool = deploy_mock_pool(
        coins,
        lp,
        A,
        gamma,
        mid_fee,
        out_fee,
        allowed_extra_profit,
        fee_gamma,
        adjustment_step,
        admin_fee,
        ma_half_time,
        [price, price],
        acc,
    )

    assert [pool.coins(i) for i in range(3)] == [coin.address for coin in coins]
    assert pool.token() == lp.address
    assert pool.A() == A
    assert pool.gamma() == gamma
    assert pool.mid_fee() == mid_fee
    assert pool.out_fee() == out_fee
    assert pool.allowed_extra_profit() == allowed_extra_profit
    assert pool.fee_gamma() == fee_gamma
    assert pool.adjustment_step() == adjustment_step
    assert pool.admin_fee() == admin_fee
    assert pool.ma_half_time() == ma_half_time
    assert [pool.price_oracle(i) for i in range(2)] == [price, price]
