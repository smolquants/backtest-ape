// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {Backtest} from "../../Backtest.sol";
import {IUniswapV3Pool} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import {IUniswapV3Factory} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
import {OracleLibrary} from "@uniswap/v3-periphery/contracts/libraries/OracleLibrary.sol";
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

    /// @notice Pushes token id to storage to track NFT positions
    function push(uint256 tokenId) external {
        tokenIds.push(tokenId);
    }

    /// @notice Reports the ETH value of the LP token using TWAP for other token
    /// @return value_ The current ETH value of the LP tokens owned by this contract
    function value() public view virtual override returns (uint256 value_) {
        for (uint256 i = 0; i < tokenIds.length; ++i) {
            uint256 tokenId = tokenIds[i];
            (, , address token0, address token1, uint24 fee, , , , , , , ) = manager.positions(tokenId);

            // get the sqrt price
            address pool = getPool(token0, token1, fee);
            uint160 sqrtRatioX96 = getSqrtRatioX96(pool);

            // get the token balances owned by LP from position manager
            (uint256 amount0, uint256 amount1) = PositionValue.total(manager, tokenId, sqrtRatioX96);

            // get the TWAP value in ETH terms of each token held by position manager
            uint256 val0 = calcAmountInETH(token0, amount0);
            uint256 val1 = calcAmountInETH(token1, amount1);

            // add to total values for all lp positions
            value_ += (val0 + val1);
        }
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

    /// @notice Gets the current tick for the pool with token0, token1, fee
    /// @return The current tick of the pool
    function getTick(address pool) public view returns (int24) {
        (, int24 tick, , , , , ) = IUniswapV3Pool(pool).slot0();
        return tick;
    }

    /// @notice Calculates the amount out in ETH terms using the ETH price for token
    /// @return amountOut_ The current ETH value for the amount in of token
    function calcAmountInETH(address token, uint256 amountIn) public view returns (uint256 amountOut_) {
        if (token == WETH9) return amountIn;

        // iterate over fee tiers for weighted average in amount out
        uint24[] memory fees = new uint24[](3);
        fees[0] = 500;
        fees[1] = 3000;
        fees[2] = 10000;

        uint256 weights;
        uint256 amountOutCumulative;
        for (uint256 i = 0; i < fees.length; ++i) {
            uint24 fee = fees[i];
            address pool = getPool(token, WETH9, fee);
            if (pool == address(0)) continue; // if no pool exists, try other fee tiers

            int24 tick = getTick(pool);
            amountOutCumulative += OracleLibrary.getQuoteAtTick(tick, uint128(amountIn), token, WETH9);
            weights++;
        }
        require(weights > 0, "token not paired with WETH in a pool");
        amountOut_ = amountOutCumulative / weights; // TODO: weight by liquidity
    }
}
