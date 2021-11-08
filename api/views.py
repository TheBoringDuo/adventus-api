from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions
# Create your views here.
from api.models import Hotel
from api.serializers import HotelsSerializer



@api_view(["GET"])
@permission_classes((permissions.IsAuthenticated,))
def getHotelsByCityID(request, cityID):
    try:
        hotels = Hotel.objects.filter(city__id = cityID)
    except Exception as e:
        print(e)
        return Response("{}")

    serializer = HotelsSerializer(hotels, many=True)

    return Response(serializer.data)
        
