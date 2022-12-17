// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.12;

import {MockUniswapV3Pool} from "./MockUniswapV3Pool.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See https://github.com/Uniswap/v3-core/blob/0.8/contracts/UniswapV3Factory.sol
contract MockUniswapV3PoolDeployer {
    struct Parameters {
        address factory;
        address token0;
        address token1;
        uint24 fee;
        int24 tickSpacing;
    }
    Parameters public parameters;

    function deploy(
        address factory,
        address token0,
        address token1,
        uint24 fee,
        int24 tickSpacing
    ) external returns (address pool) {
        parameters = Parameters({factory: factory, token0: token0, token1: token1, fee: fee, tickSpacing: tickSpacing});
        pool = address(new MockUniswapV3Pool{salt: keccak256(abi.encode(token0, token1, fee))}());
        delete parameters;
    }
}
