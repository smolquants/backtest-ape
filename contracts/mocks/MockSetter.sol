// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {Setter} from "../Setter.sol";
import {MockContract} from "./MockContract.sol";

/// @title Mock Setter
/// @notice Setter overriding a public variable in simple contract
contract MockSetter is Setter, MockContract {
    event Set(address indexed _owner);

    function set(address _owner) external {
        owner = _owner;
        emit Set(_owner);
    }
}
