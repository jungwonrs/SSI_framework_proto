// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract cmsc {
    address private owner;
    address private accessor;

    string private keyOwner;
    string private access_cmsc;

    string private hRoot;
    string private nKey;
    string private salt;
    mapping(bytes32 => bool) private usedAccessHashes;

    event return_3f(string hRoot, string Nkey, string salt);

    constructor(string memory _keyOwner) {
        owner = msg.sender;
        keyOwner = _keyOwner;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    modifier onlyAccessor() {
        require(msg.sender == accessor, "Not authorized");
        _;
    }

    function storeValues(string memory _hRoot, string memory _nKey, string memory _salt, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        hRoot = _hRoot;
        nKey = _nKey;
        salt = _salt;
    }

    function setAccessor(address _accessor, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        accessor = _accessor;
    }

    function setKeyOwner(string memory _newKeyOwner, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        keyOwner = _newKeyOwner;
    }

    function setAccessCMS(string memory _newAccessCMS, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        bytes32 access_cmsc_hash = keccak256(abi.encodePacked(_newAccessCMS));
        if (!usedAccessHashes[access_cmsc_hash]) {
            access_cmsc = _newAccessCMS;
            usedAccessHashes[access_cmsc_hash] = true;
        } else {
            revert("Accessor is already in use");
        }
    }

    function readValues(string memory _access_cmsc) public onlyAccessor {
        require(keccak256(bytes(access_cmsc)) == keccak256(bytes(_access_cmsc)), "Access_cmsc verification failed");
        access_cmsc = keyOwner;

        emit return_3f(hRoot, nKey, salt);
    }


    function readValuesbyOwner(string memory _keyOwner) public view onlyOwner returns (string memory, string memory, string memory) {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        return (hRoot, nKey, salt);
    }
}
