import os

import numpy as np
import pandas as pd
import pytest

from backtest_ape.uniswap.v3.lp import UniswapV3LPRunner


@pytest.fixture
def runner():
    tick_lower = 200280  # ~ 2000 * 1e6 USDC per 1e18 WETH
    tick_upper = 207240  # ~ 1000 * 1e6 USDC per 1e18 WETH
    amount_weth = 67000000000000000000  # 67 * 1e18 WETH
    amount_token = 34427240000  # 34,427.24 * 1e6 USDC
    return UniswapV3LPRunner(
        ref_addrs={
            "pool": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
            "manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        },
        tick_lower=tick_lower,
        tick_upper=tick_upper,
        amount_weth=amount_weth,
        amount_token=amount_token,
    )


@pytest.fixture
def path():
    p = "tests/results/uniswap/v3/lp.csv"
    if os.path.exists(p):
        os.remove(p)
    return p


def test_get_refs_state(runner):
    number = 16254713
    state = runner.get_refs_state(number)
    assert state["slot0"] == (
        2271115536847293636470521670171130,
        205279,
        785,
        1440,
        1440,
        0,
        True,
    )
    assert state["liquidity"] == 12591259481453220445
    assert state["fee_growth_global0_x128"] == 2888042077048564188809648235097692
    assert (
        state["fee_growth_global1_x128"] == 1330797012137927971917418324177509306984464
    )
    assert state["tick_info_lower"] == (
        230516823693049349,
        219847946486843875,
        1978179284235729126809955078548603,
        686326366930384297893016232932562090588936,
        6152462131364,
        198044337547992425673455364086492440599870,
        1651587340,
        True,
    )
    assert state["tick_info_upper"] == (
        3751134120809473278,
        -3747086165587011074,
        19987873086249178503837842262736,
        20984788605317380052250079237007968349421,
        17604723804,
        3779291462154278330045433,
        84814,
        True,
    )


def test_init_mocks_state(runner):
    runner.setup()
    number = 16254713
    ref_pool = runner._refs["pool"]
    state = {
        "slot0": ref_pool.slot0(block_identifier=number),
        "liquidity": 12591259481453220445,
        "fee_growth_global0_x128": 2888042077048564188809648235097692,
        "fee_growth_global1_x128": 1330797012137927971917418324177509306984464,
        "tick_info_lower": ref_pool.ticks(runner.tick_lower, block_identifier=number),
        "tick_info_upper": ref_pool.ticks(runner.tick_upper, block_identifier=number),
    }
    runner.init_mocks_state(state)

    # check position nft minted and pushed to backtest contract
    mock_manager = runner._mocks["manager"]
    token_id = 1
    assert runner._backtester.tokenIds(0) == token_id
    assert mock_manager.positions(token_id).liquidity > 0

    mock_pool = runner._mocks["pool"]
    mock_tokens = runner._mocks["tokens"]

    mock_weth = mock_tokens[0] if mock_tokens[0].symbol() == "WETH" else mock_tokens[1]
    mock_token = mock_tokens[1] if mock_tokens[0].symbol() == "WETH" else mock_tokens[0]

    # check allowances set to infinity for weth, token
    allowance_weth = mock_weth.allowance(
        runner._backtester.address, mock_manager.address
    )
    assert allowance_weth == 2**256 - 1

    allowance_token = mock_token.allowance(
        runner._backtester.address, mock_manager.address
    )
    assert allowance_token == 2**256 - 1

    # check amounts sent to pool for lp position
    balance_weth_pool = mock_weth.balanceOf(mock_pool.address)
    assert pytest.approx(balance_weth_pool) == runner.amount_weth

    balance_token_pool = mock_token.balanceOf(mock_pool.address)
    assert pytest.approx(balance_token_pool) == runner.amount_token


def test_set_mocks_state(runner):
    runner.setup()
    number = 16254713
    ref_pool = runner._refs["pool"]
    state = {
        "slot0": ref_pool.slot0(block_identifier=number),
        "liquidity": 12591259481453220445,
        "fee_growth_global0_x128": 2888042077048564188809648235097692,
        "fee_growth_global1_x128": 1330797012137927971917418324177509306984464,
        "tick_info_lower": ref_pool.ticks(runner.tick_lower, block_identifier=number),
        "tick_info_upper": ref_pool.ticks(runner.tick_upper, block_identifier=number),
    }
    runner.set_mocks_state(state)

    # check mock pool updated to given state
    mock_pool = runner._mocks["pool"]
    assert mock_pool.slot0().tick == state["slot0"].tick
    assert mock_pool.slot0().sqrtPriceX96 == state["slot0"].sqrtPriceX96
    assert mock_pool.liquidity() == state["liquidity"]
    assert mock_pool.feeGrowthGlobal0X128() == state["fee_growth_global0_x128"]
    assert mock_pool.feeGrowthGlobal1X128() == state["fee_growth_global1_x128"]
    assert (
        mock_pool.ticks(runner.tick_lower).feeGrowthOutside0X128
        == state["tick_info_lower"].feeGrowthOutside0X128
    )
    assert (
        mock_pool.ticks(runner.tick_lower).feeGrowthOutside1X128
        == state["tick_info_lower"].feeGrowthOutside1X128
    )
    assert (
        mock_pool.ticks(runner.tick_upper).feeGrowthOutside0X128
        == state["tick_info_upper"].feeGrowthOutside0X128
    )
    assert (
        mock_pool.ticks(runner.tick_upper).feeGrowthOutside1X128
        == state["tick_info_upper"].feeGrowthOutside1X128
    )


def test_record(runner, path):
    runner.setup()
    df = pd.DataFrame()
    number = 16254713
    ref_pool = runner._refs["pool"]
    state = {
        "slot0": ref_pool.slot0(block_identifier=number),
        "liquidity": 12591259481453220445,
        "fee_growth_global0_x128": 2888042077048564188809648235097692,
        "fee_growth_global1_x128": 1330797012137927971917418324177509306984464,
        "tick_info_lower": ref_pool.ticks(runner.tick_lower, block_identifier=number),
        "tick_info_upper": ref_pool.ticks(runner.tick_upper, block_identifier=number),
    }
    value = int(120 * 1e18)
    runner.record(path, number, state, value)

    # check pd dataframe has new row
    df = pd.read_csv(path)
    np.testing.assert_equal(
        list(df.columns),
        [
            "number",
            "value",
            "sqrtPriceX96",
            "liquidity",
            "feeGrowthGlobal0X128",
            "feeGrowthGlobal1X128",
            "tickLowerFeeGrowthOutside0X128",
            "tickLowerFeeGrowthOutside1X128",
            "tickUpperFeeGrowthOutside0X128",
            "tickUpperFeeGrowthOutside1X128",
        ],
    )

    row = df.iloc[0]
    assert int(row["number"]) == int(number)
    assert int(row["value"]) == int(value)
    assert int(row["sqrtPriceX96"]) == int(state["slot0"].sqrtPriceX96)
    assert int(row["liquidity"]) == int(state["liquidity"])
    assert int(row["feeGrowthGlobal0X128"]) == int(state["fee_growth_global0_x128"])
    assert int(row["feeGrowthGlobal1X128"]) == int(state["fee_growth_global1_x128"])
    assert int(row["tickLowerFeeGrowthOutside0X128"]) == int(
        state["tick_info_lower"].feeGrowthOutside0X128
    )
    assert int(row["tickLowerFeeGrowthOutside1X128"]) == int(
        state["tick_info_lower"].feeGrowthOutside1X128
    )
    assert int(row["tickUpperFeeGrowthOutside0X128"]) == int(
        state["tick_info_upper"].feeGrowthOutside0X128
    )
    assert int(row["tickUpperFeeGrowthOutside1X128"]) == int(
        state["tick_info_upper"].feeGrowthOutside1X128
    )
