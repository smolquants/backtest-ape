// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/// @title Mock Contract
/// @notice Simple contract with public storage vars
contract MockContract {
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
}

