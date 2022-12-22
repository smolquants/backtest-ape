// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

interface ICurveV2Token {
    function balanceOf(address) external view returns (uint256);

    function totalSupply() external view returns (uint256);

    function mint(address _to, uint256 _value) external returns (bool);

    function burnFrom(address _to, uint256 _value) external returns (bool);
}
