// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {Backtest} from "../../Backtest.sol";

/// @title Gearbox V2 Credit Account Backtester
/// @notice Backtests a credit account strategy reporting value in underlying token terms
contract GearboxV2CABacktest is Backtest {
    constructor() {}

    function value() public view virtual override returns (uint256 value_) {}
}
