from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

from . import sk_gen as sk
from . import recovery_sk as rsk
from . import vc_gen as vcg

from . import cmsc_control as cc
from . import vc_control as vcc

# call html view
def home(req):
    return render(req, 'home.html')

def select_page(req):
    return render(req, 'select.html')

def service_user(req):
    return render(req, 'service_user.html')

def service_provider(req):
    return render(req, 'service_provider.html')

def gen_sk(req):
    return render(req, 'gen_sk.html')

def recovery_sk(req):
    return render(req, 'recovery_sk.html')

def gen_vc(req):
    return render(req, 'gen_vc.html')

def manage_vc(req):
    return render(req, 'manage_vc.html')

#processing
def image_process(req):
    if req.method == 'POST':
        result = sk.gps_extraction(req)

        if result == "gps_duplication":
            response_data = {'message': 'Duplication error'}
            return JsonResponse(response_data, status=500)

        elif result == "no_gps_data":
            response_data = {'message': 'pictures error'}
            return JsonResponse(response_data, status=501)

        elif result == "contract_deploy_error":
            response_data = {'message': 'kcsc contract deploy error'}
            return JsonResponse(response_data, status=400)

        elif result == "pk_save_error":
            response_data = {'message': 'pk save error error'}
            return JsonResponse(response_data, status=401)

        else:
            private_key, public_key, user_address, kcsc_ad = result.split(',')
            #print(private_key)
            #print(public_key)
            #print(user_address)
            #print("log>>>>>>>>>>>>>", kcsc_ad)
            response_data = {'private_key': private_key,
                             'public_key': public_key,
                             'user_address': user_address,
                             'kcsc_address': kcsc_ad,
                             'message': 'Private key Generation is completed.'}
            return JsonResponse(response_data, status=200)

def recovery_process(req):
    if req.method == 'POST':
        kcsc_ad = req.POST.get('kcsc_address')

        result = rsk.gps_extraction(kcsc_ad, req)

        if result == "gps_duplication":
            response_data = {'message': 'Duplication error'}
            return JsonResponse(response_data, status=500)

        elif result == "no_gps_data":
            response_data = {'message': 'pictures error'}
            return JsonResponse(response_data, status=501)

        elif result == "verification_error":
            response_data = {'message': 'smart contract address error'}
            return JsonResponse(response_data, status=403)

        elif result == "not_owner":
            response_data = {'message': 'smart contract access denied'}
            return JsonResponse(response_data, status=404)

        else:
            private_key, public_key, user_address, kcsc_ad = result.split(',')

            response_data = {'private_key': private_key,
                             'public_key': public_key,
                             'user_address': user_address,
                             'kcsc_address': kcsc_ad,
                             'message': 'Private key Generation is completed.'}
            return JsonResponse(response_data, status=200)

def vc_process(req):
    if req.method == 'POST':
        result = vcg.input_process(req)

        if result == "nKey_or_salt_values_are_duplicated":
            return JsonResponse({'message': 'nKey or salt values are duplicated'}, status=500)
        elif isinstance(result, tuple):
            cmsc_ad, vccsc_ad, vc_meta = result
            return JsonResponse({'cmsc_ad': cmsc_ad, 'vccsc_ad': vccsc_ad, 'vc_meta_info': vc_meta})
        else:
            return JsonResponse({'message': 'An unknown error occurred'}, status=600)
    else:
        return HttpResponse("Invalid request method", status=405)



def get_cmsc_info(req):
    if req.method == 'POST':
        result = cc.get_cmsc_info(req)
        if isinstance(result, tuple):
            hRoot, nKey, salt = result
            return JsonResponse({'hRoot': hRoot, 'nKey': nKey, 'salt_info': salt}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)


def modify_cmsc_info(req):
    if req.method == 'POST':
        result = cc.change_3f(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

def change_access_cmsc(req):
    if req.method == 'POST':
        result = cc.change_access_cmsc(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

def change_accessor(req):
    if req.method == 'POST':
        result = cc.change_accessor(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

def change_cmsc_key_owner(req):
    if req.method == 'POST':
        result = cc.new_key_owner(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)


def get_vc_info(req):
    if req.method == 'POST':
        result = vcc.get_vc_info(req)
        if isinstance(result, tuple):
            meta, claim, pr = result
            return JsonResponse({'meta': meta, 'claim': claim, 'pr': pr}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

def get_vc_info_all(req):
    if req.method == 'POST':
        result = vcc.get_vc_info_all(req)
        if result:
            return JsonResponse({'message': 'okay', 'result': result}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)


def modify_claim_info(req):
    if req.method == 'POST':
        result = vcc.modify_claim_info(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)


def get_vc_revocation_list(req):
    if req.method == 'POST':
        result = vcc.get_vc_revocation_list(req)

        if result is None or (isinstance(result, (list, str)) and len(result) == 0):
            return JsonResponse({'message': 'empty'}, status=200)

        return JsonResponse({'message': 'okay', 'result': result}, status=200)

    else:
        return HttpResponse("Invalid request method", status=405)


def vc_revoke(req):
    if req.method == 'POST':
        result = vcc.vc_revoke(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#def change_vc_key_owner(req):

#def add_new_claim(req):

#def add_vc(req):
