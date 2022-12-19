// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.12;

import {UniswapV3Pool} from "@uniswap/v3-core/contracts/UniswapV3Pool.sol";
import {TickMath} from "@uniswap/v3-core/contracts/libraries/TickMath.sol";
import {Setter} from "../../../Setter.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See: https://github.com/Uniswap/v3-core/blob/0.8/contracts/UniswapV3Pool.sol
contract MockUniswapV3Pool is UniswapV3Pool, Setter {
    function setTick(int24 _tick) external {
        slot0.tick = _tick;
        slot0.sqrtPriceX96 = TickMath.getSqrtRatioAtTick(_tick);
    }

    function setLiquidity(uint128 _liquidity) external {
        liquidity = _liquidity;
    }

    function setFeeGrowthGlobalX128(uint256 _feeGrowthGlobal0X128, uint256 _feeGrowthGlobal1X128) external {
        feeGrowthGlobal0X128 = _feeGrowthGlobal0X128;
        feeGrowthGlobal1X128 = _feeGrowthGlobal1X128;
    }

    function setFeeGrowthOutsideX128(
        int24 _tick,
        uint256 _feeGrowthOutside0X128,
        uint256 _feeGrowthOutside1X128
    ) external {
        ticks[_tick].feeGrowthOutside0X128 = _feeGrowthOutside0X128;
        ticks[_tick].feeGrowthOutside1X128 = _feeGrowthOutside1X128;
    }
}
