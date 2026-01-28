// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/utils/Context.sol";

contract CarbonRetirement is Context {
    IERC721 public carbonCreditNFT;

    mapping(uint256 => bool) private _retiredTokens;

    event CreditRetired(address indexed by, uint256 indexed tokenId, uint256 timestamp);

    constructor(address nftAddress) {
        carbonCreditNFT = IERC721(nftAddress);
    }

    function retireCredit(uint256 tokenId) external {
        require(carbonCreditNFT.ownerOf(tokenId) == _msgSender(), "Voce neo possui este token.");
        require(!_retiredTokens[tokenId], "Este credito ja foi aposentado.");

        _retiredTokens[tokenId] = true;

        emit CreditRetired(_msgSender(), tokenId, block.timestamp);
    }

    function isRetired(uint256 tokenId) external view returns (bool) {
        return _retiredTokens[tokenId];
    }
}
