// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {Backtest} from "../../Backtest.sol";
import {IUniswapV3Pool} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import {IUniswapV3Factory} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
import {INonfungiblePositionManager} from "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";

/// @title Uniswap V3 Liquidity Provider Backtester
/// @notice Backtests an LP position in pool
abstract contract UniswapV3LPBacktest is Backtest {
    INonfungiblePositionManager public immutable manager;
    address public immutable factory;
    address public immutable WETH9;

    uint256[] public tokenIds;

    constructor(address _manager) {
        manager = INonfungiblePositionManager(_manager);
        factory = manager.factory();
        WETH9 = manager.WETH9();
    }

    /// @notice Pushes token id to storage to track NFT positions
    function push(uint256 tokenId) external {
        tokenIds.push(tokenId);
    }

    /// @notice Number of token ids pushed to list
    function count() external view returns (uint256) {
        return tokenIds.length;
    }

    /// @notice Gets the pool for token0, token1, fee
    /// @return The pool address for token0, token1, fee
    function getPool(address token0, address token1, uint24 fee) public view returns (address) {
        return IUniswapV3Factory(factory).getPool(token0, token1, fee);
    }

    /// @notice Gets the current sqrt price ratio for the pool with token0, token1, fee
    /// @return The current sqrt price ratio of the pool
    function getSqrtRatioX96(address pool) public view returns (uint160) {
        (uint160 sqrtRatioX96, , , , , , ) = IUniswapV3Pool(pool).slot0();
        return sqrtRatioX96;
    }
}
