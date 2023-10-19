// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "hardhat/console.sol";

contract SignatureDistribution {
    //mapping(address => bool) public isSigned;
    address tokenOwner;
    IERC20  token;
    uint256 modulo;

    constructor(IERC20 _tokenAddress, uint256 _modulo) {
        token = _tokenAddress;
        tokenOwner = msg.sender;
        modulo = _modulo;
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
        bytes32 _messageHash,
        bytes memory _signature,
        address _signer
    ) public {
        (bytes32 _r, bytes32 _s, uint8 _v) = splitSignature(_signature);
        address signer = ecrecover(_messageHash, _v, _r, _s);
        uint256 balance = token.balanceOf(msg.sender);


        require(signer == _signer, "Invalid signature");
        require(msg.sender == tokenOwner, "Invalid Distributor.");
        require(balance > _amount, "Insufficient balance.");
        
        // Transfer tokens to the signer
        token.transferFrom(tokenOwner,signer, _amount);
    }
}
