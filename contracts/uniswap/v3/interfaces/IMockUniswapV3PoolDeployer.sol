// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity >=0.5.0;

import {IUniswapV3PoolDeployer} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3PoolDeployer.sol";

interface IMockUniswapV3PoolDeployer is IUniswapV3PoolDeployer {
    function deploy(
        address factory,
        address token0,
        address token1,
        uint24 fee,
        int24 tickSpacing
    ) external returns (address pool);
}
