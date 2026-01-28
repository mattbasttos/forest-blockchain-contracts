// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract forestMonitor is ERC721 {
    uint256 private _nextTokenId = 1;

    struct forestRecord {
        string imageID;
        string areaName;
        string periodCurrent;
        string periodPrevious;
        string coordinates;
        uint256 deforestationArea;
        uint256 preservedArea;
        uint256 timestamp;
    }

    mapping(uint256 => forestRecord) public forestRecords;

    constructor() ERC721("forestMonitor", "Monitoramento") {}

    function createforestRecord(
        string memory imageID,
        string memory areaName,
        string memory periodCurrent,
        string memory periodPrevious,
        string memory coordinates,
        uint256 deforestationArea,
        uint256 preservedArea
    ) public returns (uint256) {
        uint256 newTokenId = _nextTokenId++;

        _mint(msg.sender, newTokenId);

        forestRecords[newTokenId] = forestRecord(
            imageID,
            areaName,
            periodCurrent,
            periodPrevious,
            coordinates,
            deforestationArea,
            preservedArea,
            block.timestamp
        );

        return newTokenId;
    }

    function getforestRecord(uint256 tokenId) public view returns (forestRecord memory) {
        ownerOf(tokenId);

        return forestRecords[tokenId];
    }
}
