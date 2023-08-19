// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.12;

import {MockUniswapV3PoolDeployer} from "./MockUniswapV3PoolDeployer.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See https://github.com/Uniswap/v3-core/blob/0.8/contracts/UniswapV3Factory.sol
contract MockUniswapV3Factory is MockUniswapV3PoolDeployer {
    mapping(address => mapping(address => mapping(uint24 => address))) public getPool;

    constructor() {}

    function feeAmountTickSpacing(uint24 fee) public view returns (int24 tickSpacing) {
        if (fee == 500) {
            tickSpacing = 10;
        } else if (fee == 3000) {
            tickSpacing = 60;
        } else if (fee == 10000) {
            tickSpacing = 200;
        }
    }

    /// @notice Overrides to deploy the mock pool
    /// @dev removes getPool storage to limit contract size
    function createPool(address tokenA, address tokenB, uint24 fee) external returns (address pool) {
        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        int24 tickSpacing = feeAmountTickSpacing(fee);
        pool = deploy(address(this), token0, token1, fee, tickSpacing);
        getPool[token0][token1][fee] = pool;
        getPool[token1][token0][fee] = pool;
    }
}
