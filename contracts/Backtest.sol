// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

abstract contract Backtest {
    constructor() {}
    
    /// @notice Executes a tx for the strategy
    function execute(address target, bytes calldata data, uint256 val) public payable returns (bytes memory result_) {
        require(val <= msg.value, "msg.value < value");
        (bool success, bytes memory result) = target.call{value: val}(data);
        if (!success) revert("failed to execute strategy");
        result_ = result;
    }
    
    /// @notice Executes multiple txs for the strategy
    function multicall(address[] calldata targets, bytes[] calldata datas, uint256[] calldata values) external payable returns (bytes[] memory results_) {
        require(targets.length == datas.length && datas.length == values.length, "tx input arrays must all be of same length");

        // init cache vars
        uint256 valueCumulative;
        results_ = new bytes[](targets.length);
        
        // loop through all inputs and execute txs
        for (uint256 i=0; i < targets.length; ++i) {
            results_[i] = execute(targets[i], datas[i], values[i]);
            valueCumulative += values[i];
        }
        require(msg.value == valueCumulative, "msg.value != sum of msg values");
    }
    
    /// @notice Reports the current value of the strategy
    /// @return The current value
    function value() public view virtual returns (uint256);

    // TODO: make super general so can set public variables
    // TODO: through wrappers on contracts targeting (for forward)
}