// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Backtest} from "../Backtest.sol";

/// @title Mock Backtest
/// @notice Strategy Backtest measuring ETH value in contract
contract MockBacktest is Backtest {
    function value() public view virtual override returns (uint256) {
        return address(this).balance;
    }

    fallback() external payable {}
}
