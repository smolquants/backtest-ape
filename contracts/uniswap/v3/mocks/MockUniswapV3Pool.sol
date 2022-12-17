// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.12;

import {UniswapV3Pool} from "@uniswap/v3-core/contracts/UniswapV3Pool.sol";
import {TickMath} from "@uniswap/v3-core/contracts/libraries/TickMath.sol";
import {Setter} from "../../../Setter.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See: https://github.com/Uniswap/v3-core/blob/0.8/contracts/UniswapV3Pool.sol
contract MockUniswapV3Pool is UniswapV3Pool, Setter {
    function setTick(int24 _tick) external {
        Slot0 memory _slot0 = slot0;
        _slot0.tick = _tick;
        _slot0.sqrtPriceX96 = TickMath.getSqrtRatioAtTick(_tick);
        slot0 = _slot0;
    }

    function setLiquidity(uint128 _liquidity) external {
        liquidity = _liquidity;
    }

    function setFeeGrowthGlobal0X128(uint256 _feeGrowthGlobal0X128) external {
        feeGrowthGlobal0X128 = _feeGrowthGlobal0X128;
    }

    function setFeeGrowthGlobal1X128(uint256 _feeGrowthGlobal1X128) external {
        feeGrowthGlobal1X128 = _feeGrowthGlobal1X128;
    }
}
