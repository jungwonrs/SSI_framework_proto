// SPDX-License-Identifier:MIT
pragma solidity ^0.8.0;

contract vccsc {
    address private owner;
    string private keyOwner;

    struct VC {
        string meta;
        string[] cl;
        string pr;
    }

    string[] private allVCs;
    mapping(string => string[]) private revokedVCList;

    mapping(string => VC) private managementTable;
    mapping(string => bool) private revokedVCs;

    constructor(string memory _keyOwner){
        owner = msg.sender;
        keyOwner = _keyOwner;
    }

    modifier onlyOwner (){
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    function storeVc(string memory _meta, string[] memory _cl, string memory _pr, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "error");

        for (uint i=0; i < _cl.length; i++ ){
            if (revokedVCs[_cl[i]]) revert("This VC is revoked and cannot be stored.");
        }

        VC memory newVC = VC({
            meta: _meta,
            cl: _cl,
            pr: _pr
        });

        managementTable[_meta] = newVC;
        allVCs.push(_meta);
    }

    function readAllVC(string memory _keyOwner) public view onlyOwner returns (VC[] memory ) {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "error");

        VC[] memory vcArray = new VC[](allVCs.length);

        for (uint i = 0; i < allVCs.length; i++){
            vcArray[i] = managementTable[allVCs[i]];
        }
        return vcArray;
    }

    function readVC(string memory _meta) public view returns(VC memory) {
        return managementTable[_meta];
    }

    function revokeVC(string memory _meta, string memory _cl, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        VC storage vcToUpdate = managementTable[_meta];

        for (uint i = 0; i < vcToUpdate.cl.length; i++) {
            if (keccak256(bytes(vcToUpdate.cl[i])) == keccak256(bytes(_cl))) {
                revokedVCs[_cl] = true;
                revokedVCList[_meta].push(_cl); // Add to revoked list under the meta key
                vcToUpdate.cl[i] = ""; // Set the element to empty string
                break;
            }
        }
    }

    function revokeVClist(string memory _meta, string memory _keyOwner) public view onlyOwner returns (string[] memory) {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        return revokedVCList[_meta]; // Return the list of revoked VCs for the given meta value
    }


    function updateVC(string memory _meta, string[] memory _newCl, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        VC storage vcToUpdate = managementTable[_meta];

        for (uint i = 0; i < _newCl.length; i++) {
            if (revokedVCs[_newCl[i]]) {
                revert("Cannot update with a previously revoked VC");
            }
        }
        vcToUpdate.cl = _newCl; // Update the entire cl array
    }

    function addCl(string memory _meta, string memory _cl, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        if (revokedVCs[_cl]) {
            revert("Cannot add a revoked VC");
        }

        VC storage vcToUpdate = managementTable[_meta];
        vcToUpdate.cl.push(_cl);
    }

    function setKeyOwner(string memory _newKeyOwner, string memory _keyOwner) public onlyOwner {
        require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
        keyOwner = _newKeyOwner;
    }

}
