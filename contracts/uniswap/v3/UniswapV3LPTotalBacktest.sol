// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {UniswapV3LPBacktest} from "./UniswapV3LPBacktest.sol";
import {MockPositionValue as PositionValue} from "./mocks/libraries/MockPositionValue.sol";

/// @title Uniswap V3 Liquidity Provider Total Backtester
/// @notice Backtests an LP position in pool reporting total (token0, token1) values (fees + principal) of LP tokens
contract UniswapV3LPTotalBacktest is UniswapV3LPBacktest {
    constructor(address _manager) UniswapV3LPBacktest(_manager) {}

    /// @notice Reports the total (token0, token1) values of the LP tokens owned by this contract
    /// @return values_ The current (token0, token1) values of the LP tokens owned by this contract
    function values() public view virtual override returns (uint256[] memory values_) {
        values_ = new uint256[](2);
        for (uint256 i = 0; i < tokenIds.length; ++i) {
            uint256 tokenId = tokenIds[i];
            (, , address token0, address token1, uint24 fee, , , , , , , ) = manager.positions(tokenId);

            // get the sqrt price
            address pool = getPool(token0, token1, fee);
            uint160 sqrtRatioX96 = getSqrtRatioX96(pool);

            (uint256 amount0Total, uint256 amount1Total) = PositionValue.total(manager, tokenId, sqrtRatioX96);
            values_[0] += amount0Total;
            values_[1] += amount1Total;
        }
    }
}
