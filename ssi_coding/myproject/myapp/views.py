from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from . import sk_gen as sk
from . import recovery_sk as rsk
from . import vc_gen as vcg

from . import cmsc_control as cc
from . import vc_control as vcc

from . import sp_service as sp

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

#/user/sk/imageprocess
@swagger_auto_schema(
    method='POST',
    operation_description="This API \'try it out\' doesn't work. please use prototype web view. ",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image': openapi.Schema(
                type=openapi.TYPE_FILE,
                description='Image to upload.',
                required=['true']  # If the image is mandatory
            ),

        },
        required=['image']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        500: openapi.Response('Duplication error.'),
        501: openapi.Response('pictures error'),
        403: openapi.Response('smart contract address error'),
        404: openapi.Response('smart contract access denied'),
    }
)
@api_view(['POST'])
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
#/user/sk/recovery/process
@swagger_auto_schema(
    method='POST',
    operation_description="This API \'try it out\' doesn't work. please use prototype web view. ",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'image': openapi.Schema(
                type=openapi.TYPE_FILE,
                description='Image to upload.',
                required=['true']  # If the image is mandatory
            ),

        },
        required=['image']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        500: openapi.Response('Duplication error.'),
        501: openapi.Response('pictures error'),
        403: openapi.Response('smart contract address error'),
        404: openapi.Response('smart contract access denied'),
    }
)
@api_view(['POST'])
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

#/user/genvc/process
@swagger_auto_schema(
    method='POST',
    operation_description="vc_process",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'Blockchain_sk': openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'Blockchain_ad' : openapi.Schema(type=openapi.TYPE_STRING, description='The address input from the form.'),
            'Nkey': openapi.Schema(type=openapi.TYPE_STRING, description='The Nkey input from the form.'),
            'Salt': openapi.Schema(type=openapi.TYPE_STRING, description='The salt input from the form.'),
            'key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'access_cmsc': openapi.Schema(type=openapi.TYPE_STRING, description='The access CMSC input from the form.'),
            'vccscData': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC Data input from the form.'),

        },
        required=['Blockchain_sk', 'Blockchain_ad', 'Nkey', 'Salt', 'key_owner', 'access_cmsc', 'vccscData']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'cmsc_ad': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'vccsc_ad': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'vc_meta_info': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
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

#/user/manvc/getCmscInfo
@swagger_auto_schema(
    method='POST',
    operation_description="get_cmsc_info",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmscAddress': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'key_owner_cmsc' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'private_key': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
        },
        required=['cmscAddress', 'key_owner_cmsc', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'hRoot': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'nKey': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'salt_info': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
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

#/user/manvc/modifyCmscInfo
@swagger_auto_schema(
    method='POST',
    operation_description="modify_cmsc_info",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'HRoot': openapi.Schema(type=openapi.TYPE_STRING, description='The new HRoot input from the form.'),
            'Nkey': openapi.Schema(type=openapi.TYPE_STRING, description='The new Nkey input from the form.'),
            'Salt': openapi.Schema(type=openapi.TYPE_STRING, description='The new Salt input from the form.'),
        },
        required=['cmsc_ad', 'private_key', 'key_owner', 'HRoot', 'Nkey', 'Salt']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def modify_cmsc_info(req):
    if req.method == 'POST':
        result = cc.change_3f(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/changeAccessCmsc
@swagger_auto_schema(
    method='POST',
    operation_description="change_access_cmsc",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'new_access_cmsc': openapi.Schema(type=openapi.TYPE_STRING, description='The new access cmsc input from the form.'),

        },
        required=['cmsc_ad', 'private_key', 'key_owner', 'new_access_cmsc']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def change_access_cmsc(req):
    if req.method == 'POST':
        result = cc.change_access_cmsc(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/changeAccessor
@swagger_auto_schema(
    method='POST',
    operation_description="change_accessor",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'cmscAccessor': openapi.Schema(type=openapi.TYPE_STRING, description='The cmsc accessor input from the form.'),

        },
        required=['cmsc_ad', 'private_key', 'key_owner', 'cmscAccessor']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def change_accessor(req):
    if req.method == 'POST':
        result = cc.change_accessor(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/changeCmscKeyOwner
@swagger_auto_schema(
    method='POST',
    operation_description="change_cmsc_key_owner",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'new_key_owner': openapi.Schema(type=openapi.TYPE_STRING, description='The new key owner input from the form.'),

        },
        required=['cmsc_ad', 'private_key', 'key_owner', 'new_key_owner']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def change_cmsc_key_owner(req):
    if req.method == 'POST':
        result = cc.new_key_owner(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)

        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/getVcInfo
@swagger_auto_schema(
    method='POST',
    operation_description="get_vc_info",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccscAddress': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'vc_meta' : openapi.Schema(type=openapi.TYPE_STRING, description='The VC meta owner input from the form.'),
        },
        required=['vccscAddress', 'vc_meta']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'meta': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'claim': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                    'pr': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
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

#/user/manvc/getVcInfoAll
@swagger_auto_schema(
    method='POST',
    operation_description="get vc info all",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccscAddress': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'key_owner' : openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC key owner input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),

        },
        required=['vccsc_ad', 'key_owner', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'result': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)

@api_view(['POST'])
def get_vc_info_all(req):
    if req.method == 'POST':
        result = vcc.get_vc_info_all(req)
        if result:
            return JsonResponse({'message': 'okay', 'result': result}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/modifyClaimInfo
@swagger_auto_schema(
    method='POST',
    operation_description="modify claim info",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'vccsc_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC key owner input from the form.'),
            'cmsc_ad' : openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'cmsc_key': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC key owner input from the form.'),
            'private_key': openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
            'vc_meta': openapi.Schema(type=openapi.TYPE_STRING, description='The vc meta input from the form.'),
            'vcc_data': openapi.Schema(type=openapi.TYPE_STRING, description='The vc data input from the form.'),

        },
        required=['vccsc_ad', 'key_owner', 'cmsc_ad', 'cmsc_key', 'private_key', 'vc_meta', 'vcc_data']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def modify_claim_info(req):
    if req.method == 'POST':
        result = vcc.modify_claim_info(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/getVcRevocationList
@swagger_auto_schema(
    method='POST',
    operation_description="get vc revocation list",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccscAddress': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'key_owner' : openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'vc_meta' : openapi.Schema(type=openapi.TYPE_STRING, description='The vc meta input from the form.'),
            'private_key': openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
        },
        required=['vccsc_ad', 'key_owner', 'vc_meta', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def get_vc_revocation_list(req):
    if req.method == 'POST':
        result = vcc.get_vc_revocation_list(req)

        if result is None or (isinstance(result, (list, str)) and len(result) == 0):
            return JsonResponse({'message': 'empty'}, status=200)

        return JsonResponse({'message': 'okay', 'result': result}, status=200)

    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/vcRevoke
@swagger_auto_schema(
    method='post',
    operation_description="VC revoke",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'key_owner' : openapi.Schema(type=openapi.TYPE_STRING, description='The key owner input from the form.'),
            'vc_meta' : openapi.Schema(type=openapi.TYPE_STRING, description='The vc meta input from the form.'),
            'cl': openapi.Schema(type=openapi.TYPE_STRING, description='The claim meta input from the form.'),
            'private_key': openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
        },
        required=['vccsc_ad', 'key_owner', 'vc_meta', 'cl', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def vc_revoke(req):
    if req.method == 'POST':
        result = vcc.vc_revoke(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/changeVccscKeyOwner
@swagger_auto_schema(
    method='post',
    operation_description="change vc key owner",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'orignal_key_owner' : openapi.Schema(type=openapi.TYPE_STRING, description='The original key owner input from the form.'),
            'new_key_owner' : openapi.Schema(type=openapi.TYPE_STRING, description='The new key owner input from the form.'),
            'private_key': openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
        },
        required=['vccsc_ad', 'orignal_key_owner', 'new_key_owner', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def change_vc_key_owner(req):
    if req.method == 'POST':
        result = vcc.change_vc_key_owner(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/addNewVC
@swagger_auto_schema(
    method='post',
    operation_description="add new VC",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'vccsc_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC KEY input from the form.'),
            'cmsc_ad' : openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'cmsc_key': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC KEY input from the form.'),
            'vc_data' : openapi.Schema(type=openapi.TYPE_STRING, description='The VC data address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
        },
        required=['vccsc_ad', 'vccsc_key', 'cmsc_ad', 'cmsc_key', 'vc_data', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'result_meta': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def add_vc(req):
    if req.method == 'POST':
        result = vcc.add_vc(req)
        if result:
            return JsonResponse({'message': 'okay', 'result_meta': result}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/user/manvc/addNewClaim
@swagger_auto_schema(
    method='post',
    operation_description="add new claim",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC address input from the form.'),
            'vccsc_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC KEY input from the form.'),
            'cmsc_ad' : openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'cmsc_key': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC KEY input from the form.'),
            'vc_meta' : openapi.Schema(type=openapi.TYPE_STRING, description='The VC meta input from the form.'),
            'vc_data' : openapi.Schema(type=openapi.TYPE_STRING, description='The VC data address input from the form.'),
            'private_key' : openapi.Schema(type=openapi.TYPE_STRING, description='The private key input from the form.'),
        },
        required=['vccsc_ad', 'vccsc_key', 'cmsc_ad', 'cmsc_key', 'vc_meta', 'vc_data', 'private_key']
    ),
    responses ={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def add_new_claim(req):
    if req.method == 'POST':
        result = vcc.add_new_claim(req)
        if result:
            return JsonResponse({'message': 'okay'}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)

#/sp/verify
@swagger_auto_schema(
    method='post',
    operation_description="Processes data from the service provider form.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cmsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The CMSC address input from the form.'),
            'access_cmsc': openapi.Schema(type=openapi.TYPE_STRING, description='The Access CMSC input from the form.'),
            'vccsc_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The VCCSC Address input from the form.'),
            'vc_meta': openapi.Schema(type=openapi.TYPE_STRING, description='The VC meta input from the form.'),
            'u_ad': openapi.Schema(type=openapi.TYPE_STRING, description='The User Address input from the form.'),
            'sp_sk': openapi.Schema(type=openapi.TYPE_STRING, description='The Service Provider Private Key input from the form.')
        },
        required=['cmsc_ad', 'access_cmsc', 'vccsc_ad', 'vc_meta', 'u_ad', 'sp_sk']
    ),
    responses={
        200: openapi.Response(
            description="Data processed successfully with result metadata.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message'),
                    'result_meta': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='The result of the user verification process'
                    ),
                },
                example={
                    'message': 'okay',
                    'result_meta': 'Example result metadata'
                }
            )
        ),
        406: openapi.Response(
            description="An error occurred during the call.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Status message')
                },
                example={
                    'message': 'call error'
                }
            )
        ),
        405: openapi.Response('Invalid request method.')
    }
)
@api_view(['POST'])
def user_verify(req):
    if req.method == 'POST':
        result = sp.user_verify(req)
        print("result ->>> ", result)
        if result:
            return JsonResponse({'message': 'okay', 'result_meta': result}, status=200)
        else:
            return JsonResponse({'message': 'call error'}, status=406)
    else:
        return HttpResponse("Invalid request method", status=405)