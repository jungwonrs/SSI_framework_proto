import json
from web3 import Web3
from solcx import compile_source
from eth_account import Account

from . import cmsc_control as cc
from . import vc_gen as vcg



def blockchain_connect(sc_ad):
    w3 = Web3(Web3.HTTPProvider('http://163.239.201.32:8545'))
    solc_version = "0.8.0"

    contract_source_code = """
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
    """
    compiled_sol = compile_source(contract_source_code, solc_version=solc_version)
    contract_interface = compiled_sol['<stdin>:vccsc']

    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        address=sc_ad
    )

    return w3, contract


def get_vc_info(req):

    json_req_data = json.loads(req.body.decode('utf-8'))

    vccsc_address = json_req_data.get('vccscAddress')
    vc_meta = json_req_data.get('vc_meta')

    w3, contract = blockchain_connect(vccsc_address)

    data_vc = contract.functions.readVC(vc_meta).call()

    meta, claim, pr = data_vc


    return meta, claim, pr

def get_vc_info_all(req):
    json_req_data = json.loads(req.body.decode('utf-8'))
    vccsc_address = json_req_data.get('vccscAddress')
    key_owner = json_req_data.get('key_owner')
    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    w3, contract = blockchain_connect(vccsc_address)

    data_vc = contract.functions.readAllVC(key_owner).call({
        'from': wallet_ad
    })

    return data_vc

def modify_claim_info(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    vccsc_ad = json_req_data.get('vccsc_ad')
    vccsc_key = json_req_data.get('vccsc_key')

    cmsc_ad = json_req_data.get('cmsc_ad')
    cmsc_key = json_req_data.get('cmsc_key')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    vc_meta = json_req_data.get('vc_meta')
    vcc_data = json_req_data.get('vcc_data')


    _, cmsc = cc.blockchain_connect(cmsc_ad)

    data_vc = cmsc.functions.readValuesbyOwner(cmsc_key).call({
        'from': wallet_ad
    })

    hRoot = data_vc[0]
    nKey = [item.strip(" '") for item in data_vc[1].strip("[]").split(',')]
    salt = [item.strip(" '") for item in data_vc[2].strip("[]").split(',')]

    new_claim = vcg.gen_claim(vcc_data, hRoot, nKey, salt)

    new_cl_list = [new_claim]

    w3, vccsc = blockchain_connect(vccsc_ad)

    vccsc_data = vccsc.functions.updateVC(vc_meta, new_cl_list, vccsc_key).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    vccsc_data_signed_transaction = w3.eth.account.sign_transaction(vccsc_data, private_key=private_key)
    vccsc_data_tx_hash = w3.eth.send_raw_transaction(vccsc_data_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(vccsc_data_tx_hash)


    if receipt.status == 1:
        return True
    else:
        return False

def get_vc_revocation_list(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    vccsc_ad = json_req_data.get('vccscAddress')
    key_owner = json_req_data.get('key_owner')
    meta = json_req_data.get('vc_meta')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    w3, contract = blockchain_connect(vccsc_ad)

    contract_data = contract.functions.revokeVClist(meta, key_owner).call({
        'from': wallet_ad
    })

    print(contract_data)

    return contract_data

def vc_revoke(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    vccsc_ad = json_req_data.get('vccsc_ad')
    key_owner = json_req_data.get('key_owner')
    meta = json_req_data.get('vc_meta')
    cl = json_req_data.get('cl')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    w3, contract = blockchain_connect(vccsc_ad)

    vccsc_data = contract.functions.revokeVC(meta, cl, key_owner).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    vccsc_data_signed_transaction = w3.eth.account.sign_transaction(vccsc_data, private_key=private_key)
    vccsc_data_tx_hash = w3.eth.send_raw_transaction(vccsc_data_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(vccsc_data_tx_hash)


    if receipt.status == 1:
        return True
    else:
        return False


