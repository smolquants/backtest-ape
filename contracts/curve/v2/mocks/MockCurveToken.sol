// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockCurveToken is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address _to, uint256 _value) external returns (bool) {
        _mint(_to, _value);
        return true;
    }

    /// @notice Increases supply by factory of (1 + frac/1e18) and mints it for _to
    function mint_relative(address _to, uint256 frac) external returns (uint256) {
        uint256 supply = totalSupply();
        uint256 ds = (supply * frac) / 1e18;
        if (ds == 0) return 0;

        // mint the new supply and return amount minted
        _mint(_to, ds);
        return ds;
    }

    function burnFrom(address _to, uint256 _value) external returns (bool) {
        _burn(_to, _value);
        return true;
    }
}
