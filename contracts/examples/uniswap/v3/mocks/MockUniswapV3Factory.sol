// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.12;

import {IMockUniswapV3PoolDeployer} from "../interfaces/IMockUniswapV3PoolDeployer.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See https://github.com/Uniswap/v3-core/blob/0.8/contracts/UniswapV3Factory.sol
contract MockUniswapV3Factory {
    address public owner;
    IMockUniswapV3PoolDeployer public deployer;
    mapping(uint24 => int24) public feeAmountTickSpacing;
    mapping(address => mapping(address => mapping(uint24 => address))) public getPool;

    constructor(address _deployer) {
        // deployer separated out for contract size issues
        deployer = IMockUniswapV3PoolDeployer(_deployer);

        // orig v3 params
        owner = msg.sender;
        feeAmountTickSpacing[500] = 10;
        feeAmountTickSpacing[3000] = 60;
        feeAmountTickSpacing[10000] = 200;
    }

    /// @notice Overrides to deploy the mock pool
    function createPool(address tokenA, address tokenB, uint24 fee) external returns (address pool) {
        require(tokenA != tokenB);
        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        require(token0 != address(0));
        int24 tickSpacing = feeAmountTickSpacing[fee];
        require(tickSpacing != 0);
        require(getPool[token0][token1][fee] == address(0));
        pool = deployer.deploy(address(this), token0, token1, fee, tickSpacing);
        getPool[token0][token1][fee] = pool;
        // populate mapping in the reverse direction, deliberate choice to avoid the cost of comparing addresses
        getPool[token1][token0][fee] = pool;
    }
}
