// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Setter Wrapper
/// @notice Abstract Setter wrapper to set public variables on mock versions of existing contracts
abstract contract Setter {
    constructor() {}

    /// @notice Makes internal calls to the setter
    /// @param datas The calldatas to call the setter with
    /// @return results_ The results of the internal calls
    function calls(bytes[] calldata datas) external returns (bytes[] memory results_) {
        // init cache var
        results_ = new bytes[](datas.length);

        // loop through all inputs and make internal calls
        for (uint256 i = 0; i < datas.length; i++) {
            (bool success, bytes memory result) = address(this).delegatecall(datas[i]);
            if (!success) revert("failed to make internal calls");
            results_[i] = result;
        }
    }
}
