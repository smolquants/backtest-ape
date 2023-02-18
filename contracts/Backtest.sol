// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title Backtest Strategy Wrapper
/// @notice Abstract Backtest wrapper to execute on-chain strategies through for back (and forward) testing
abstract contract Backtest {
    constructor() {}

    /// @notice Executes a tx for the strategy
    /// @dev See https://github.com/Uniswap/v3-periphery/blob/main/contracts/base/Multicall.sol
    /// @param target The address of the contract to call
    /// @param data The calldata to call the target with
    /// @param val The msg.value to pay the target
    /// @return result_ The result of the call
    function execute(address target, bytes calldata data, uint256 val) public payable returns (bytes memory result_) {
        require(val <= msg.value, "msg.value < value");
        (bool success, bytes memory result) = target.call{value: val}(data);
        if (!success) {
            // Next 5 lines from https://ethereum.stackexchange.com/a/83577
            if (result.length < 68) revert("failed to execute strategy");
            assembly {
                result := add(result, 0x04)
            }
            revert(abi.decode(result, (string)));
        }
        result_ = result;
    }

    /// @notice Executes multiple txs for the strategy
    /// @param targets The addresses of the contracts to call
    /// @param datas The calldatas to call each target with
    /// @param values The msg.values to pay each target
    /// @return results_ The results of each call
    function multicall(
        address[] calldata targets,
        bytes[] calldata datas,
        uint256[] calldata values
    ) external payable returns (bytes[] memory results_) {
        require(
            targets.length == datas.length && datas.length == values.length,
            "tx input arrays must all be of same length"
        );

        // init cache vars
        uint256 valueCumulative;
        results_ = new bytes[](targets.length);

        // loop through all inputs and execute txs
        for (uint256 i = 0; i < targets.length; ++i) {
            results_[i] = execute(targets[i], datas[i], values[i]);
            valueCumulative += values[i];
        }
        require(msg.value == valueCumulative, "msg.value != sum of msg values");
    }

    /// @notice Reports the current value of the strategy
    /// @return The current value
    function value() public view virtual returns (uint256);
}
