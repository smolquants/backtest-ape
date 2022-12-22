// SPDX-License-Identifier: MIT
pragma solidity 0.8.17;

import {Backtest} from "../../Backtest.sol";
import {ICurveV2Pool} from "./interfaces/ICurveV2Pool.sol";
import {ICurveV2Token} from "./interfaces/ICurveV2Token.sol";

/// @title Curve Tricrypto Liquidity Provider Backtester
/// @notice Backtests an LP position in pool reporting value of LP tokens in USDT terms
contract CurveTricryptoLPBacktest is Backtest {
    ICurveV2Pool public immutable pool;
    ICurveV2Token public immutable lp;

    constructor(address _pool) {
        pool = ICurveV2Pool(_pool);
        lp = ICurveV2Token(pool.token());
    }

    /// @notice Reports the USDT value of the LP token
    /// @return value_ The current USDT value of the LP tokens owned by this contract
    function value() public view virtual override returns (uint256 value_) {
        uint256 amount = lp.balanceOf(address(this));
        uint256 totalSupply = lp.totalSupply();

        // adjust amount for rounding
        // See https://github.com/curvefi/tricrypto-ng/blob/main/contracts/old/CurveCryptoSwap.vy#L844
        amount -= 1;

        // underlying token balances owned are pro-rata share w.r.t. lp amount of total tokens in pool
        for (uint256 i = 0; i < 3; ++i) {
            uint256 balance = (pool.balances(i) * amount) / totalSupply;
            if (i == 0) {
                value_ += balance;
                continue;
            }

            // convert values to USDT denom using oracle price
            uint256 price = pool.price_oracle(i - 1);
            value_ += ((price * balance) / 1e30); // 1e18 * 1e12 for mulDiv then convert to 6 decimals
        }
    }
}
