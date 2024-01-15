import json
import hashlib
import random
import string
from web3 import Web3
from solcx import compile_source
from eth_account.messages import encode_defunct
import ecies

def input_process(req):
    w3 = Web3(Web3.HTTPProvider('http://163.239.201.32:8545'))

    json_req_data = json.loads(req.body.decode('utf-8'))

    sk = json_req_data.get("Blockchain_sk")
    ad = json_req_data.get("Blockchain_ad")
    hRoot = json_req_data.get("HRoot")
    nKey = json_req_data.get("Nkey")
    salt = json_req_data.get('Salt')
    key_owner = json_req_data.get("key_owner")
    access_cmsc = json_req_data.get("access_cmsc")
    vc_claim = json_req_data.get("vccscData")

    nKey_dpulication_check = duplication_check(nKey)
    salt_duplication_check = duplication_check(salt)

    if not nKey_dpulication_check and not salt_duplication_check:
        claim = gen_claim(vc_claim, hRoot, nKey, salt)

        # generate cmsc
        cmsc_ad = deploy_cmsc(w3, ad, sk, hRoot, nKey, salt, key_owner, access_cmsc)

        # generate metadata
        meta = metadata_gen(10)

        # generate pr
        meta_claim = claim + meta
        message_hash = Web3.keccak(text=meta_claim).hex()

        message_hash_bytes = bytes.fromhex(message_hash[2:])  # Skip the '0x' part
        signable_message = encode_defunct(message_hash_bytes)
        pr = w3.eth.account.sign_message(signable_message, private_key=sk)

        # generate vccsc
        vccsc_ad = deploy_vccsc(w3, ad, sk, claim, meta, pr, key_owner)

        return cmsc_ad, vccsc_ad, meta

    else:
        return "nKey_or_salt_values_are_duplicated"

def deploy_vccsc(w3, ad, sk, claim, meta, pr, key_owner):
    try:
        wallet_ad = ad
        user_sk = sk

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

        complied_sol = compile_source(contract_source_code, solc_version=solc_version)
        contract_interface = complied_sol['<stdin>:vccsc']

        contract = w3.eth.contract(
            abi = contract_interface['abi'],
            bytecode = contract_interface['bin']
        )

        transaction_data = contract.constructor(key_owner).build_transaction({
            'chainId': 1008,
            'gas': 3000000,
            'gasPrice': 0,
            'nonce': w3.eth.get_transaction_count(wallet_ad)
        })

        signed_transaction = w3.eth.account.sign_transaction(transaction_data, private_key=user_sk)
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        vccsc_address = w3.eth.get_transaction_receipt(tx_hash)['contractAddress']

        print("vccsc_address>>>>>", vccsc_address)

        result = save_vc(w3, user_sk, wallet_ad, claim, meta, pr, vccsc_address, contract_interface, key_owner)

        return result

    except Exception as e:
        print("Error:", e)
        return "contract_deploy_error"

def save_vc(w3, user_sk, wallet_ad, claim, meta, pr, contract_ad, contract_interface, key_owner):
    try:
        contract_access = w3.eth.contract(
            abi=contract_interface['abi'],
            address=contract_ad
        )

        multi_cl = [claim]

        data_vc = contract_access.functions.storeVc(str(meta), multi_cl, str(pr), key_owner).build_transaction({
            'from': wallet_ad,
            'gas': 3000000,
            'gasPrice': 0,
            'nonce':  w3.eth.get_transaction_count(wallet_ad)
        })

        data_vc_signed_transaction = w3.eth.account.sign_transaction(data_vc, private_key=user_sk)
        data_vc_tx_hash = w3.eth.send_raw_transaction(data_vc_signed_transaction.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(data_vc_tx_hash)
        print("receipt_save_vc>>>>>", receipt)

        return contract_ad


    except Exception as e:
        print("Error:", e)
        return "contract_deploy_error"


def metadata_gen(length):
    try:
        characters = string.ascii_letters + string.digits + string.punctuation
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    except Exception as e:
        print("Error:", e)
        return "contract_deploy_error"

def deploy_cmsc(w3, ad, sk, hRoot, nKey, salt, key_owner, access_cmsc):
    try:
        wallet_ad = ad
        user_sk = sk

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
            abi = contract_interface['abi'],
            bytecode = contract_interface['bin']
        )
        transction_data = contract.constructor(key_owner).build_transaction({
            'chainId': 1008,
            'gas': 3000000,
            'gasPrice': 0,
            'nonce': w3.eth.get_transaction_count(wallet_ad)
        })

        signed_transaction = w3.eth.account.sign_transaction(transction_data, private_key=user_sk)
        tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)
        cmsc_contract_address = w3.eth.get_transaction_receipt(tx_hash)['contractAddress']

        print("cmsc_address>>>>", cmsc_contract_address)
        result = save_3f(w3, user_sk, wallet_ad, hRoot, nKey, salt, contract_interface, cmsc_contract_address, access_cmsc, key_owner)

        return result

    except Exception as e:
        print("Error:", e)
        return "contract_deploy_error"


def save_3f(w3, user_sk, wallet_ad, hRoot, nKey, salt, contract_interface, contract_ad, access_cmsc, key_owner):
    try:
        contract_access = w3.eth.contract(
            abi=contract_interface['abi'],
            address=contract_ad
        )

        data_3f = contract_access.functions.storeValues(hRoot, str(nKey), str(salt), key_owner).build_transaction({
            'from': wallet_ad,
            'gas': 3000000,
            'gasPrice': 0,
            'nonce':  w3.eth.get_transaction_count(wallet_ad)
        })

        data_3f_signed_transaction = w3.eth.account.sign_transaction(data_3f, private_key=user_sk)
        data_3f_tx_hash = w3.eth.send_raw_transaction(data_3f_signed_transaction.rawTransaction)
        receipt1 = w3.eth.wait_for_transaction_receipt(data_3f_tx_hash)
        print("receipt_3f>>>>>", receipt1)

        data_access_cmsc = contract_access.functions.setAccessCMS(access_cmsc, key_owner).build_transaction({
            'from': wallet_ad,
            'gas': 3000000,
            'gasPrice': 0,
            'nonce': w3.eth.get_transaction_count(wallet_ad)
        })

        data_access_cmsc_signed_tranaction = w3.eth.account.sign_transaction(data_access_cmsc, private_key=user_sk)
        data_access_cms_tx_hash = w3.eth.send_raw_transaction(data_access_cmsc_signed_tranaction.rawTransaction)
        receipt2 = w3.eth.wait_for_transaction_receipt(data_access_cms_tx_hash)
        print("receipt_access_cms>>>>>", receipt2)

        return contract_ad

    except Exception as e:
        print("Error:", e)
        return "3f_save_error"


def duplication_check(lst):
    seen = set()
    for item in lst:
        if item in seen:
            return True
        seen.add(item)
    return False


def gen_claim(vc_claim, hRoot, nKey, salt):
    #generate rule table
    new_nKey = [int(x) for x in nKey]
    sorted_indices = sorted(range(len(new_nKey)), key=lambda k: new_nKey[k])
    sorted_salt = [salt[idx] for idx in sorted_indices]
    second_row = calculate_second_row(hRoot, new_nKey)


    table = [
        ['0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111', '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'],
        second_row,
        sorted_salt
    ]

    binary_string = ''.join(format(ord(char), '08b') for char in vc_claim)

    split_value = [binary_string[i:i + 4] for i in range(0, len(binary_string), 4)]
    #print("log2>>>>>>>>>>>>>>", split_value)

    first_to_second = [second_row[table[0].index(bit)] for bit in split_value]
    #print("log3>>>>>>>>>>>>>>", first_to_second)

    transformed_claim = [sorted_salt[second_row.index(value)] for value in first_to_second]
    #print("log4>>>>>>>>>>>>>>", transformed_claim)

    transformed_claim_str = ''.join(transformed_claim)
    #print("log5>>>>>>>>>>>>>>", transformed_claim_str)
    transformed_claim_hex= to_hex_string(transformed_claim_str)
    #print("log6>>>>>>>>>>>>>>", transformed_claim_hex)


    xor_result = xor_two_strings(transformed_claim_hex, hRoot)
    #print("log7>>>>>>>>>>>>>>",xor_result)

    return xor_result

def to_hex_string(s):
    return ''.join(format(ord(c), '02x') for c in s)

def xor_two_strings(s1, s2):
    if not isinstance(s1, str) or not isinstance(s2, str):
        raise TypeError("Inputs must be strings.")
    try:
        int(s1, 16)
        int(s2, 16)
    except ValueError:
        raise ValueError("One of the input strings is not a valid hex string.")

    if len(s1) > len(s2):
        s2 = s2.ljust(len(s1), '0')
    else:
        s1 = s1.ljust(len(s2), '0')

    return ''.join([f"{(int(a, 16) ^ int(b, 16)):x}" for a, b in zip(s1, s2)])


def calculate_second_row(hRoot, nKey):
    second_row = []
    for i in nKey:
        current_hash = hRoot
        for _ in range(i):
            current_hash = hashlib.sha256(current_hash.encode()).hexdigest()
        second_row.append(current_hash)

    return second_row


