import os

import numpy as np
import pandas as pd
import pytest

from backtest_ape.curve.v2.lp import CurveV2LPRunner


@pytest.fixture
def runner():
    amount_usd = int(1e12)  # 1M USD
    amount_weth = int((1e24 / 1218668363989192860592) * 1e18)
    amount_wbtc = int((1e24 / 16816946825680501806263) * 1e8)
    amounts = [amount_usd, amount_wbtc, amount_weth]
    return CurveV2LPRunner(
        ref_addrs={"pool": "0xD51a44d3FaE010294C616388b506AcdA1bfAAE46"},
        num_coins=len(amounts),
        amounts=amounts,
    )


@pytest.fixture
def path():
    p = "tests/results/curve/v2/lp.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner):
    number = 16254713
    state = runner.get_refs_state(number)
    assert state["balances"] == [51444788313173, 306130683764, 42421274934619665540607]
    assert state["D"] == 154655480528709339739900799
    assert state["A_gamma"] == [
        183752478137306770270222288013175834186240000,
        581076037942835227425498917514114728328226821,
        1633548703,
        0,
    ]
    assert state["prices"] == [
        16816946825680501806263,
        1218668363989192860592,
    ]
    assert state["total_supply"] == 183341149725574822964704


def test_init_mocks_state(runner):
    runner.setup()
    mock_pool = runner._mocks["pool"]
    mock_lp = runner._mocks["lp"]
    mock_coins = runner._mocks["coins"]

    state = {
        "balances": [
            51444788313173,
            306130683764,
            42421274934619665540607,
        ],
        "D": 154655480528709339739900799,
        "A_gamma": [
            183752478137306770270222288013175834186240000,
            581076037942835227425498917514114728328226821,
            1633548703,
            0,
        ],
        "prices": [
            16816946825680501806263,
            1218668363989192860592,
        ],
        "total_supply": 183341149725574822964704,
    }
    runner.init_mocks_state(state)

    coin_balances = []
    for i, mock_coin in enumerate(mock_coins):
        # check tokens minted
        supply = mock_coin.totalSupply()
        assert supply == runner.amounts[i]

        # check pool approved to spend from backtester
        allowance = mock_coin.allowance(runner._backtester.address, mock_pool.address)
        assert allowance == 2**256 - 1

        # check coin balances in pool for liquidity added
        coin_balances.append(mock_coin.balanceOf(mock_pool.address))
        assert coin_balances[i] == runner.amounts[i]

        # check total supply of LP token remains same but with tokens to backtester
        assert mock_lp.totalSupply() == state["total_supply"]

        minted = state["total_supply"] - mock_lp.balanceOf(runner._acc.address)
        assert mock_lp.balanceOf(runner._backtester.address) == minted
        assert mock_lp.balanceOf(runner._backtester.address) > 0


def test_set_mocks_state(runner):
    runner.setup()
    state = {
        "balances": [
            51444788313173,
            306130683764,
            42421274934619665540607,
        ],
        "D": 154655480528709339739900799,
        "A_gamma": [
            183752478137306770270222288013175834186240000,
            581076037942835227425498917514114728328226821,
            1633548703,
            0,
        ],
        "prices": [
            16816946825680501806263,
            1218668363989192860592,
        ],
        "total_supply": 183341149725574822964704,
    }
    runner.set_mocks_state(state)

    # check mock pool updated to given state
    mock_pool = runner._mocks["pool"]
    mock_lp = runner._mocks["lp"]
    assert [mock_pool.balances(i) for i in range(runner.num_coins)] == state["balances"]
    assert mock_pool.D() == state["D"]
    assert [
        mock_pool.initial_A_gamma(),
        mock_pool.future_A_gamma(),
        mock_pool.initial_A_gamma_time(),
        mock_pool.future_A_gamma_time(),
    ] == state["A_gamma"]
    assert [mock_pool.price_oracle(i) for i in range(runner.num_coins - 1)] == state[
        "prices"
    ]

    # check mock lp supply minted to runner acc
    assert mock_lp.balanceOf(runner._acc.address) == state["total_supply"]

    # modify total supply state and check burned difference from runner acc
    state["total_supply"] -= 100
    runner.set_mocks_state(state)
    assert mock_lp.balanceOf(runner._acc.address) == state["total_supply"]


def test_record(runner, path):
    runner.setup()

    df = pd.DataFrame()
    number = 16254713
    state = {
        "balances": [
            51444788313173,
            306130683764,
            42421274934619665540607,
        ],
        "D": 154655480528709339739900799,
        "A_gamma": [
            183752478137306770270222288013175834186240000,
            581076037942835227425498917514114728328226821,
            1633548703,
            0,
        ],
        "prices": [
            16816946825680501806263,
            1218668363989192860592,
        ],
        "total_supply": 183341149725574822964704,
    }
    value = 3000000000
    runner.record(path, number, state, value)

    # check pd dataframe has new row
    df = pd.read_csv(path)
    np.testing.assert_equal(
        list(df.columns),
        [
            "number",
            "value",
            "D",
            "total_supply",
            "balances0",
            "balances1",
            "balances2",
            "A_gamma0",
            "A_gamma1",
            "A_gamma2",
            "A_gamma3",
            "prices0",
            "prices1",
        ],
    )

    row = df.iloc[0]
    assert int(row["number"]) == int(number)
    assert int(row["value"]) == int(value)
    assert int(row["D"]) == int(state["D"])
    assert int(row["total_supply"]) == int(state["total_supply"])
    assert int(row["balances0"]) == int(state["balances"][0])
    assert int(row["balances1"]) == int(state["balances"][1])
    assert int(row["balances2"]) == int(state["balances"][2])
    assert int(row["A_gamma0"]) == int(state["A_gamma"][0])
    assert int(row["A_gamma1"]) == int(state["A_gamma"][1])
    assert int(row["A_gamma2"]) == int(state["A_gamma"][2])
    assert int(row["A_gamma3"]) == int(state["A_gamma"][3])
    assert int(row["prices0"]) == int(state["prices"][0])
    assert int(row["prices1"]) == int(state["prices"][1])
