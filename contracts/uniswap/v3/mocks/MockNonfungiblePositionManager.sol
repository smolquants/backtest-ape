// SPDX-License-Identifier: GPL-2.0-or-later
pragma solidity 0.8.15;

import {NonfungiblePositionManager} from "@uniswap/v3-periphery/contracts/NonfungiblePositionManager.sol";

/// @dev DO NOT ACTUALLY DEPLOY
/// @dev See https://github.com/Uniswap/v3-periphery/blob/0.8/contracts/NonfungiblePositionManager.sol
contract MockNonfungiblePositionManager is NonfungiblePositionManager {
    constructor(address _factory, address _WETH9) NonfungiblePositionManager(_factory, _WETH9, address(0)) {}
}
