// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import {Setter} from "../../../Setter.sol";

contract MockAggregatorV3 is Setter, AggregatorV3Interface {
    uint8 public immutable decimals;
    uint256 public immutable version;
    string public description;

    struct RoundData {
        uint80 roundId;
        int256 answer;
        uint256 startedAt;
        uint256 updatedAt;
        uint80 answeredInRound;
    }
    mapping(uint80 => RoundData) public rounds;
    uint80 public latestRoundId;

    constructor(string memory _description, uint8 _decimals, uint256 _version) {
        description = _description;
        decimals = _decimals;
        version = _version;
    }

    function getRoundData(
        uint80 _roundId
    )
        public
        view
        returns (uint80 roundId_, int256 answer_, uint256 startedAt_, uint256 updatedAt_, uint80 answeredInRound_)
    {
        RoundData memory round = rounds[_roundId];
        (roundId_, answer_, startedAt_, updatedAt_, answeredInRound_) = (
            round.roundId,
            round.answer,
            round.startedAt,
            round.updatedAt,
            round.answeredInRound
        );
    }

    function latestRoundData() public view returns (uint80, int256, uint256, uint256, uint80) {
        return getRoundData(latestRoundId);
    }

    function setRound(RoundData memory _round) external {
        rounds[_round.roundId] = _round;
    }

    function setLatestRoundId(uint80 _roundId) external {
        require(rounds[_roundId].roundId == _roundId, "round does not exist");
        latestRoundId = _roundId;
    }
}
