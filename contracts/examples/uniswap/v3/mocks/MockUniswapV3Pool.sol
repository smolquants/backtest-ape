// SPDX-License-Identifier: MIT
pragma solidity 0.8.12;

import {Setter} from "../../../../Setter.sol";
import {UniswapV3Pool} from "@uniswap/v3-core/contracts/UniswapV3Pool.sol";

contract MockUniswapV3Pool is UniswapV3Pool, Setter {
    function setSlot0(Slot0 memory _slot0) external {
        slot0 = _slot0;
    }

    function setFeeGrowthGlobal0X128(uint256 _feeGrowthGlobal0X128) external {
        feeGrowthGlobal0X128 = _feeGrowthGlobal0X128;
    }

    function setFeeGrowthGlobal1X128(uint256 _feeGrowthGlobal1X128) external {
        feeGrowthGlobal1X128 = _feeGrowthGlobal1X128;
    }
}
