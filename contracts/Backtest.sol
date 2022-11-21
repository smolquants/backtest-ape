// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

abstract contract Backtest {
    constructor() {}
    
    /// @notice Reports the current value of the strategy
    /// @return The current value
    function value() public view virtual returns (uint256);
    
    // TODO: make super general so can set public variables
    // TODO: through wrappers on contracts targeting
}