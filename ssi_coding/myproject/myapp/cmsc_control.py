import json
from web3 import Web3
from solcx import compile_source
from eth_account import Account

def blockchain_connect(sc_ad):
    w3 = Web3(Web3.HTTPProvider('http://163.239.201.32:8545'))
    solc_version = "0.8.0"

    contract_source_code = """
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
    
        function readValues(string memory _access_cmsc) public onlyAccessor returns (string memory, string memory, string memory) {
            require(keccak256(bytes(access_cmsc)) == keccak256(bytes(_access_cmsc)), "Access_cmsc verification failed");
            access_cmsc = keyOwner;
            return (hRoot, nKey, salt);
        }
    
    
        function readValuesbyOwner(string memory _keyOwner) public view onlyOwner returns (string memory, string memory, string memory) {
            require(keccak256(bytes(keyOwner)) == keccak256(bytes(_keyOwner)), "Key owner verification failed");
            return (hRoot, nKey, salt);
        }
    }
    """
    compiled_sol = compile_source(contract_source_code, solc_version=solc_version)
    contract_interface = compiled_sol['<stdin>:cmsc']

    contract = w3.eth.contract(
        abi=contract_interface['abi'],
        address=sc_ad
    )

    return w3, contract



def get_cmsc_info(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_address = json_req_data.get('cmscAddress')
    key_owner = json_req_data.get('key_owner_cmsc')
    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    w3, contract = blockchain_connect(cmsc_address)

    data_vc = contract.functions.readValuesbyOwner(key_owner).call({
        'from': wallet_ad
    })

    hRoot = data_vc[0]
    nKey = [item.strip(" '") for item in data_vc[1].strip("[]").split(',')]
    salt = [item.strip(" '") for item in data_vc[2].strip("[]").split(',')]

    return hRoot, nKey, salt

def change_3f(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_ad = json_req_data.get('cmsc_ad')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    key_owner = json_req_data.get('key_owner')
    hRoot = json_req_data.get('HRoot')
    nKey = json_req_data.get('Nkey')
    salt = json_req_data.get('Salt')

    w3, contract = blockchain_connect(cmsc_ad)

    data_3f = contract.functions.storeValues(hRoot, str(nKey), str(salt), key_owner).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    data_3f_signed_transaction = w3.eth.account.sign_transaction(data_3f, private_key=private_key)
    data_3f_tx_hash = w3.eth.send_raw_transaction(data_3f_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(data_3f_tx_hash)

    if receipt.status == 1:
        return True
    else:
        return False

def change_access_cmsc(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_ad = json_req_data.get('cmsc_ad')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    key_owner = json_req_data.get('key_owner')
    new_access_cmsc = json_req_data.get('new_access_cmsc')

    w3, contract = blockchain_connect(cmsc_ad)

    data_3f = contract.functions.setAccessCMS(new_access_cmsc, key_owner).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    data_3f_signed_transaction = w3.eth.account.sign_transaction(data_3f, private_key=private_key)
    data_3f_tx_hash = w3.eth.send_raw_transaction(data_3f_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(data_3f_tx_hash)

    if receipt.status == 1:
        return True
    else:
        return False

def change_accessor(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_ad = json_req_data.get('cmsc_ad')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    key_owner = json_req_data.get('key_owner')
    new_accessor = json_req_data.get('cmscAccessor')

    w3, contract = blockchain_connect(cmsc_ad)

    data_3f = contract.functions.setAccessor(new_accessor, key_owner).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    data_3f_signed_transaction = w3.eth.account.sign_transaction(data_3f, private_key=private_key)
    data_3f_tx_hash = w3.eth.send_raw_transaction(data_3f_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(data_3f_tx_hash)

    if receipt.status == 1:
        return True
    else:
        return False

def new_key_owner(req):
    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_ad = json_req_data.get('cmsc_ad')

    private_key = json_req_data.get('private_key')
    account = Account.from_key(private_key)
    wallet_ad = account.address

    key_owner = json_req_data.get('key_owner')
    new_key = json_req_data.get('new_key_owner')

    w3, contract = blockchain_connect(cmsc_ad)

    data_3f = contract.functions.setKeyOwner(new_key, key_owner).build_transaction({
        'from': wallet_ad,
        'gas': 3000000,
        'gasPrice': 0,
        'nonce': w3.eth.get_transaction_count(wallet_ad)
    })

    data_3f_signed_transaction = w3.eth.account.sign_transaction(data_3f, private_key=private_key)
    data_3f_tx_hash = w3.eth.send_raw_transaction(data_3f_signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(data_3f_tx_hash)

    if receipt.status == 1:
        return True
    else:
        return False
