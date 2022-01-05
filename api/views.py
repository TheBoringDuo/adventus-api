from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions, generics
# Create your views here.
from api.models import Hotel, City, Country, User
from api.serializers import HotelsSerializer, CitySerializer, RegisterSerializer, BusinessRegisterSerializer
from django.http import HttpResponse
from .permissions import CanAddBusinessObjects

@api_view(["GET"])
# @permission_classes((permissions.IsAuthenticated,))
def getHotelsByCityID(request, cityID, limitResults = -1):
    try:
        if limitResults == -1:
            hotels = Hotel.objects.filter(city__id = cityID)
        else:
            hotels = Hotel.objects.filter(city__id = cityID, pk__lte = limitResults)
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


class RegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = RegisterSerializer
	

class BusinessRegisterView(generics.CreateAPIView):
	queryset = User.objects.all()
	serializer_class = BusinessRegisterSerializer

@api_view(['GET'])
@permission_classes((CanAddBusinessObjects,))
def testView(request):
    return HttpResponse("Business Client")
