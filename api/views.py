from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions
# Create your views here.
from api.models import Hotel, City, Country
from api.serializers import HotelsSerializer, CitySerializer



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
       

@api_view(["GET"])
def getAllCitiesByCountryOrNot(request):
    country = request.GET.get('country', None)
    try:
        if country != None:
            country = Country.objects.filter(name__contains=country)[0]
    except:
        country = None
    
    if country != None:
        cities = City.objects.filter(country=country)
    else:
        cities = City.objects.all()

    serializer = CitySerializer(cities, many=True)
    print(country)
    return Response(serializer.data)
