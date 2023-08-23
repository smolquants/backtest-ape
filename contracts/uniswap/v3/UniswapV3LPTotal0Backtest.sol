// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {UniswapV3LPBacktest} from "./UniswapV3LPBacktest.sol";
import {PositionValue} from "@uniswap/v3-periphery/contracts/libraries/PositionValue.sol";

/// @title Uniswap V3 Liquidity Provider Token0 Total Backtester
/// @notice Backtests an LP position in pool reporting total token0 value (fees + principal) of LP tokens
contract UniswapV3LPTotal0Backtest is UniswapV3LPBacktest {
    constructor(address _manager) UniswapV3LPBacktest(_manager) {}

    /// @notice Reports the total token0 value of the LP tokens owned by this contract
    /// @return value_ The current token0 value of the LP tokens owned by this contract
    function value() public view virtual override returns (uint256 value_) {
        for (uint256 i = 0; i < tokenIds.length; ++i) {
            uint256 tokenId = tokenIds[i];
            (, , address token0, address token1, uint24 fee, , , , , , , ) = manager.positions(tokenId);

            // get the sqrt price
            address pool = getPool(token0, token1, fee);
            uint160 sqrtRatioX96 = getSqrtRatioX96(pool);

            (uint256 amount0Total, uint256 amount1Total) = PositionValue.total(manager, tokenId, sqrtRatioX96);
            value_ += amount0Total;
        }
    }
}
