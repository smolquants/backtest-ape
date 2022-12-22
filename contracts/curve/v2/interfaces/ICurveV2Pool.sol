// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

interface ICurveV2Pool {
    function coins(uint256) external view returns (address);

    function balances(uint256) external view returns (uint256);

    function price_oracle(uint256 k) external view returns (uint256);

    function token() external view returns (address);
}
