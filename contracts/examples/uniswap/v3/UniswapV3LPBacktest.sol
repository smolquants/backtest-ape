// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import {Backtest} from "../../../Backtest.sol";
import {IUniswapV3Pool} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import {OracleLibrary} from "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";
import {PoolAddress} from "@uniswap/v3-periphery/contracts/libraries/PoolAddress.sol";
import {PositionValue} from "@uniswap/v3-periphery/contracts/libraries/PositionValue.sol";
import {INonfungiblePositionManager} from "@uniswap/v3-periphery/contracts/interfaces/INonfungiblePositionManager.sol";

/// @title Uniswap V3 Liquidity Provider Backtester
/// @notice Backtests an LP position in pool reporting value of LP tokens in ETH terms
contract UniswapV3LPBacktest is Backtest {
    INonfungiblePositionManager public immutable manager;
    address public immutable factory;
    address public immutable WETH9;

    uint256[] public tokenIds;

    constructor(address _manager) {
        manager = INonfungiblePositionManager(_manager);
        factory = manager.factory();
        WETH9 = manager.WETH9();
    }
    
    /// @notice Reports the ETH value of the LP token using TWAP for other token
    /// @return value_ The current ETH value of the LP tokens owned by this contract
    function value() public view virtual override returns (uint256 value_) {
        for (uint256 i = 0; i < tokenIds.length; ++i) {
            uint256 tokenId = tokenIds[i];
            (,, address token0, address token1, uint24 fee,,,,,,,) = manager.positions(tokenId);
            uint160 sqrtRatioX96 = getSqrtRatioX96(token0, token1, fee);
            
            // get the token balances owned by LP from position manager
            (uint256 amount0, uint256 amount1) = PositionValue.total(manager, tokenId, sqrtRatioX96);
            
            // get the TWAP value in ETH terms of each token held by position manager
            uint256 val0 = calcAmountInETH(token0, amount0);
            uint256 val1 = calcAmountInETH(token1, amount1);
            
            // add to total values for all lp positions
            value_ += (val0 + val1);
        }
    }
    
    function getSqrtRatioX96(address token0, address token1, uint24 fee) public view returns (uint160) {
        PoolAddress.PoolKey memory poolKey = PoolAddress.PoolKey({
            token0: token0,
            token1: token1,
            fee: fee
        });
        IUniswapV3Pool pool = IUniswapV3Pool(PoolAddress.computeAddress(factory, poolKey));
        (uint160 sqrtRatioX96,,,,,,) = pool.slot0();
        return sqrtRatioX96;
    }
    
    /// @notice Calculates the amount out in ETH terms using the ETH price for token
    /// @return The current ETH value for the amount in of token
    function calcAmountInETH(address token, uint256 amountIn) public view returns (uint256) {
        if (token == WETH9) return amountIn;
        
        // TODO: ...
        return 0;
    }
}

