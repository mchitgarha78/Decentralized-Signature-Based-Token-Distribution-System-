// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    address public owner;

    constructor(string memory name, string memory symbol) ERC20(name, symbol) {
        owner = msg.sender;
        _mint(msg.sender, 1000000 * 10 ** 18); // Mint 1,000,000 tokens to the contract creator
    }

    // This function allows the owner to mint more tokens
    function mint(address to, uint256 amount) public {
        require(msg.sender == owner, "Only the owner can mint tokens");
        _mint(to, amount);
    }
}