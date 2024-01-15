from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from eth_account import Account
import hashlib
from web3 import Web3
from solcx import compile_source

def gps_extraction(kcsc_ad, req):
    uploaded_images = []

    for i in range(1, 11):
        image_name = f'image{i}'
        if image_name in req.FILES:
            uploaded_image = req.FILES[image_name]
            uploaded_images.append(uploaded_image)

    gps_info_list = []

    for uploaded_image in uploaded_images:
        # GPS decimal place settings
        gps_info = extract_gps_info(uploaded_image, 6)
        if gps_info is not None:
            gps_info_list.append(gps_info)

    if has_duplicates(gps_info_list):
        return "gps_duplication"
    else:
        if not gps_info_list:
            return "no_gps_data"

        seed_data = ",".join([str(info) for info in gps_info_list]).encode('utf-8')
        seed = hashlib.sha256(seed_data).digest()
        sk, pk, ad = generate_key(seed)

        result = kcsc_confirm(pk, ad, kcsc_ad)

        if result == "verification_error":
            return "verification_error"

        if result == "not_owner":
            return "not_owner"

        if result == "verification_okay":
            return f"{sk},{pk},{ad},{kcsc_ad}"

def kcsc_confirm(pk, ad, kcsc_ad):
    try:
        w3 = Web3(Web3.HTTPProvider('http://163.239.201.32:8545'))
        solc_version = "0.8.0"

        contract_source_code = """
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
        """


        compiled_sol = compile_source(contract_source_code, solc_version=solc_version)
        contract_interface = compiled_sol['<stdin>:kcsc']

        contract = w3.eth.contract(
            abi=contract_interface['abi'],
            address=kcsc_ad
        )

        pk_call = contract.functions.getPublicKey().call()
        owner_call = contract.functions.owner().call()

        if owner_call == ad:
            if pk_call == pk:
                print("log>>>>>>>>>>>>> recovery completed")
                return "verification_okay"

        else:
            return "not_owner"

    except Exception as e:
        print("Error:", e)
        return "verification_error"


def generate_key(seed):
    sk = Account.from_key(seed)
    sk_hex = sk.key.hex()

    pk = sk._key_obj.public_key.to_hex()

    ad = sk.address

    return sk_hex, pk, ad


def extract_gps_info(image_file, decimal_places):
    image = Image.open(image_file)
    exif_data = image._getexif()
    gps_info = None

    if exif_data:
        for tag, value in exif_data.items():
            if TAGS.get(tag) == 'GPSInfo':
                gps_info = value
                break

    if gps_info:
        latitude = gps_info[2][0] + gps_info[2][1] / 60 + gps_info[2][2] / 3600
        longitude = gps_info[4][0] + gps_info[4][1] / 60 + gps_info[4][2] / 3600

        latitude = round(latitude, decimal_places)
        longitude = round(longitude, decimal_places)

        latitude = float(latitude)
        longitude = float(longitude)

        return {'latitude': latitude, 'longitude': longitude}
    else:
        return None


def has_duplicates(gps_info_list):
    seen = set()
    for gps_info in gps_info_list:
        gps_info_str = str(gps_info)
        if gps_info_str in seen:
            return True
        seen.add(gps_info_str)
    return False
