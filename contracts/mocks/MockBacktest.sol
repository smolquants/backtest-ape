// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Backtest} from "../Backtest.sol";

/// @title Mock Backtest
/// @notice Strategy Backtest measuring ETH value in contract
contract MockBacktest is Backtest {
    function values() public view virtual override returns (uint256[] memory) {
        uint256[] memory vs = new uint256[](1);
        vs[0] = address(this).balance;
        return vs;
    }

    fallback() external payable {}
}
