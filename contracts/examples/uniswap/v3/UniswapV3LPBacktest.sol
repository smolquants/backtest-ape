// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import {Backtest} from "../../../Backtest.sol";
import {OracleLibrary} from "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";
import {INonfungiblePositionManager} from "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";

/// @title Uniswap V3 Liquidity Provider Backtester
/// @notice Backtests an LP position in pool reporting value of LP tokens in ETH terms
contract UniswapV3LPBacktest is Backtest {
    address public immutable positionManager;
    address public immutable pool;

    constructor(address _positionManager, address _pool) {
        positionManager = _positionManager;
        pool = _pool;
    }
    
    /// @notice Reports the ETH value of the LP token using TWAP for other token
    function value() public view virtual override returns (uint256) {
        return 0;
    }
}

