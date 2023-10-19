// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "hardhat/console.sol";


contract SignatureDistribution {
    //mapping(address => bool) public isSigned;
    address tokenOwner;
    IERC20  token;
    mapping (address => bool) nodeWallets;
    constructor(IERC20 _tokenAddress) {
        token = _tokenAddress;
        tokenOwner = msg.sender;
        nodeWallets[0xDbfd7D50ed5D8CfA61eed64267FABE02d70231Db] = true;
        nodeWallets[0x1D1821d08ADA5aF3F48119BbBf193C865da020dE] = true;
        nodeWallets[0x1050297611775cC7ec729572C217f774CE9e53f7] = true;
    }

    function splitSignature(
        bytes memory sig
    ) public pure returns (bytes32 r, bytes32 s, uint8 v) {
        require(sig.length == 65, "invalid signature length");

        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
    }

    function verifyAndDistribute(
        uint256 _amount,
        bytes memory _signature
    ) public {
        require(nodeWallets[msg.sender] == true, "Invalid signer.");
        
        bytes32 messageHash = keccak256(abi.encodePacked(msg.sender, _amount));
        bytes32 ethSignedMessageHash = keccak256(
                abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash));
        (bytes32 r, bytes32 s, uint8 v) = splitSignature(_signature);
        address signer = ecrecover(ethSignedMessageHash, v, r, s);
        uint256 balance = token.balanceOf(tokenOwner);


        require(signer == msg.sender, "Invalid signature");
        require(balance > _amount, "Insufficient balance.");
        
        // Transfer tokens to the signer
        token.transferFrom(tokenOwner,signer, _amount);
    }
}
