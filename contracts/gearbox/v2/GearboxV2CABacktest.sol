// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {Backtest} from "../../Backtest.sol";
import {ICreditFacade} from "@gearbox/core-v2/contracts/interfaces/ICreditFacade.sol";
import {ICreditManagerV2} from "@gearbox/core-v2/contracts/interfaces/ICreditManagerV2.sol";

/// @title Gearbox V2 Credit Account Backtester
/// @notice Backtests a credit account strategy reporting value in underlying token terms
contract GearboxV2CABacktest is Backtest {
    address public immutable facade;
    address public immutable manager;

    constructor(address _facade, address _manager) {
        facade = _facade;
        manager = _manager;
    }

    /// @notice Reports the current value of the credit account
    /// @return value_ The current value of the credit account
    function value() public view virtual override returns (uint256 value_) {
        address account = ICreditManagerV2(manager).creditAccounts(address(this));
        (value_,) = ICreditFacade(facade).calcTotalValue(account);
    }
}
