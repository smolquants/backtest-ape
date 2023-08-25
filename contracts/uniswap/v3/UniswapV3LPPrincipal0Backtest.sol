// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {UniswapV3LPBacktest} from "./UniswapV3LPBacktest.sol";
import {MockPositionValue as PositionValue} from "./mocks/libraries/MockPositionValue.sol";

/// @title Uniswap V3 Liquidity Provider Token0 Principal Backtester
/// @notice Backtests an LP position in pool reporting principal token0 value of LP tokens
contract UniswapV3LPPrincipal0Backtest is UniswapV3LPBacktest {
    constructor(address _manager) UniswapV3LPBacktest(_manager) {}

    /// @notice Reports the principal token0 value of the LP tokens owned by this contract
    /// @return value_ The current token0 principal of the LP tokens owned by this contract
    function value() public view virtual override returns (uint256 value_) {
        for (uint256 i = 0; i < tokenIds.length; ++i) {
            uint256 tokenId = tokenIds[i];
            (, , address token0, address token1, uint24 fee, , , , , , , ) = manager.positions(tokenId);

            // get the sqrt price
            address pool = getPool(token0, token1, fee);
            uint160 sqrtRatioX96 = getSqrtRatioX96(pool);

            (uint256 amount0Principal, uint256 amount1Principal) = PositionValue.principal(
                manager,
                tokenId,
                sqrtRatioX96
            );
            value_ += amount0Principal;
        }
    }
}
