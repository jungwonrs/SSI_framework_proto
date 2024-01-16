import json
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import hashlib
import ast


from . import cmsc_control as cc
from . import vc_control as vc

def user_verify(req):

    json_req_data = json.loads(req.body.decode('utf-8'))

    cmsc_ad = json_req_data.get('cmsc_ad')
    access_cmsc = json_req_data.get('access_cmsc')
    vccsc_ad = json_req_data.get('vccsc_ad')
    vc_meta = json_req_data.get('vc_meta')
    user_ad = json_req_data.get('u_ad')

    sp_sk = json_req_data.get('sp_sk')
    account = Account.from_key(sp_sk)
    sp_wallet_ad = account.address

    _, cmsc = cc.blockchain_connect(cmsc_ad)
    w3, vccsc = vc.blockchain_connect(vccsc_ad)

    vc_data = vccsc.functions.readVC(vc_meta).call()

    meta, claim, pr = vc_data

    signature_hex_str = pr.split("signature=HexBytes('")[1].split("')")[0]

    for cl in claim:
        meta_claim = cl + meta
        message_hash = Web3.keccak(text=meta_claim).hex()

        message_hash_bytes = bytes.fromhex(message_hash[2:])
        signable_message = encode_defunct(message_hash_bytes)

        recovered_address = w3.eth.account.recover_message(signable_message, signature=signature_hex_str)

        if recovered_address == user_ad:

            data_cmsc = cmsc.functions.readValues(access_cmsc).build_transaction({
                'from': sp_wallet_ad,
                'gas': 3000000,
                'gasPrice': 0,
                'nonce': w3.eth.get_transaction_count(sp_wallet_ad)
            })

            vccsc_data_signed_transaction = w3.eth.account.sign_transaction(data_cmsc, private_key=sp_sk)
            vccsc_data_tx_hash = w3.eth.send_raw_transaction(vccsc_data_signed_transaction.rawTransaction)
            receipt = w3.eth.wait_for_transaction_receipt(vccsc_data_tx_hash)

            if receipt.status == 1:
                logs = cmsc.events.return_3f().get_logs(fromBlock=w3.eth.block_number)
                for log in logs:
                    hRoot = log.args.hRoot
                    nKey = log.args.Nkey
                    salt = log.args.salt
                    claim = decrypt_claim(cl, hRoot, nKey, salt)
                    return claim
            else:
                return False

        else:
            return False


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

def decrypt_claim(xor_result, hRoot, nKey_str, salt_str):
    nKey = ast.literal_eval(nKey_str)
    salt = ast.literal_eval(salt_str)

    original_hex = xor_two_strings(xor_result, hRoot)
    original_str = bytes.fromhex(original_hex).decode('utf-8', errors='ignore')

    new_nKey = [int(x) for x in nKey]
    sorted_indices = sorted(range(len(new_nKey)), key=lambda k: new_nKey[k])
    sorted_salt = [salt[idx] for idx in sorted_indices]
    second_row = calculate_second_row(hRoot, new_nKey)

    table = [
        ['0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111', '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'],
        second_row,
        sorted_salt
    ]

    second_row_transformation = []
    i = 0
    while i < len(original_str):
        matched = False
        for salt_value in sorted_salt:
            if original_str.startswith(salt_value, i):
                second_row_transformation.append(second_row[sorted_salt.index(salt_value)])
                i += len(salt_value)
                matched = True
                break
        if not matched:
            print(f"Unmatched character sequence starting at position {i}")
            return None

    binary_string = ''.join([table[0][table[1].index(sec_row)] for sec_row in second_row_transformation])

    split_binary = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    decrypted_claim = ''.join([chr(int(b, 2)) for b in split_binary])

    return decrypted_claim


