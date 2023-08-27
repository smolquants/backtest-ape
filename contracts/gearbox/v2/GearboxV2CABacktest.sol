// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import {Backtest} from "../../Backtest.sol";
import {ICreditFacade} from "@gearbox/core-v2/contracts/interfaces/ICreditFacade.sol";
import {ICreditManagerV2} from "@gearbox/core-v2/contracts/interfaces/ICreditManagerV2.sol";

/// @title Gearbox V2 Credit Account Backtester
/// @notice Backtests a credit account strategy reporting value in underlying token terms
contract GearboxV2CABacktest is Backtest {
    address public immutable manager;

    constructor(address _manager) {
        manager = _manager;
    }

    /// @notice Reports the current health factor of the credit account
    /// @return values_ The current health factor of the credit account
    function values() public view virtual override returns (uint256[] memory values_) {
        address facade = ICreditManagerV2(manager).creditFacade();
        address account = ICreditManagerV2(manager).creditAccounts(address(this));
        values_ = new uint256[](1);
        values_[0] = ICreditFacade(facade).calcCreditAccountHealthFactor(account);
    }
}
