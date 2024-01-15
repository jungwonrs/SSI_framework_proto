// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract kcsc {
    address public owner;
    string public publicKey;

    event PublicKeyUpdated(string indexed newPublicKey);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    function updatePublicKey(string memory _newPublicKey) public onlyOwner {
        publicKey = _newPublicKey;
        emit PublicKeyUpdated(_newPublicKey);
    }

    function getPublicKey() public view returns (string memory) {
        return publicKey;
    }
}
