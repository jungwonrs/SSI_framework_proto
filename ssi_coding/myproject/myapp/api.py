from django.http import JsonResponse
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Hello, API!', schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
)
@api_view(['GET'])
def api_hello(request):
    data = {'message': 'Hello, API!'}
    return JsonResponse(data)

#Create SK with 10 GPS values


#Recover sk with 10 gps values

#Create Vc


#
