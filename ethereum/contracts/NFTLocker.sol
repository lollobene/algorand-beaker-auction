// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract NFTLocker {

  bool internal locked;

  address public owner;
  address public winner;

  uint256 public releaseTime;

  event TokenLocked(address token, uint256 tokenId);
  event TokenUnlocked(address token, uint256 tokenId);
  event Winner(address winner);

  constructor() {}

  modifier onlyOwner() {
    require(owner == msg.sender, "ERROR: ONLY OWNER");
     _;
  }

  function approveContract(address token, uint256 tokenId) external {
    IERC721(token).approve(address(this), tokenId);
  }

  function Lock(address token, uint256 tokenId, uint256 _releaseTime) external {
    require(IERC721(token).getApproved(tokenId) == address(this), "Locker Contract Not Approved.");
    IERC721(token).transferFrom((msg.sender), address(this), tokenId);
    releaseTime = _releaseTime;
    emit TokenLocked(token, tokenId);
  }

  function setWinner(address _winner) external {
    winner = _winner;
    emit Winner(_winner);
  }

  function Unlock(address token, uint256 tokenId) external {
    require(block.timestamp > releaseTime, "Too early to unlock.");
    require(msg.sender == winner, "You are not the winner.");
    IERC721(token).transferFrom(address(this), winner, tokenId);
    emit TokenUnlocked(token, tokenId);
  }
}