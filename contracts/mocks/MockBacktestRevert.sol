// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Backtest} from "../Backtest.sol";

/// @title Mock Backtest Revert
/// @notice Strategy Backtest reverts on call to values()
contract MockBacktestRevert is Backtest {
    function values() public view virtual override returns (uint256[] memory) {
        revert("Failed to get values");
    }

    fallback() external payable {}
}
