from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions, generics
# Create your views here.
from api.models import Hotel, City, Country, User
from api.serializers import HotelsSerializer, CitySerializer, RegisterSerializer, BusinessRegisterSerializer, HotelSerializer
from api.serializers import RegisterHotelSerializer, TagsSerializer
from django.http import HttpResponse
from .permissions import CanAddBusinessObjects, CanEditBusinessObject
from taggit.models import Tag
from rest_framework.mixins import UpdateModelMixin

@api_view(["GET"])
# @permission_classes((permissions.IsAuthenticated,))
def getHotelsByCityID(request, cityID, limitResults = -1):
    try:
        if limitResults == -1:
            hotels = Hotel.objects.filter(city__id = cityID, active=True, listed=True)
        else:
            hotels = Hotel.objects.filter(city__id = cityID, pk__lte = limitResults, active=True, listed=True)
    except Exception as e:
        print(e)
        return Response("{}")

    serializer = HotelsSerializer(hotels, many=True)

    return Response(serializer.data)

@api_view(["GET"])
def getHotelByID(request, hotelID):
    try:
        hotel = Hotel.objects.get(id=hotelID, active=True)
        print(hotel)
    except Exception as e:
        print(e)
        return Response("{}")

    serializer = HotelSerializer(hotel)
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

@api_view(["GET"])
def getHotelsByCityAndTags(request, cityID):
    tags = request.GET.get('tags', None)
    if tags is None:
        return Response("{}")
    else:
        tags = tags.split(',')
        hotels = Hotel.objects.filter(city__id=cityID, tags__name__in=tags, active=True).distinct()
        if hotels is not None:
            serializer = HotelsSerializer(hotels, many=True)
            return Response(serializer.data)
        else:
            return Response("{}")

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

@permission_classes((CanAddBusinessObjects,permissions.IsAuthenticated,))
class RegisterHotelView(generics.CreateAPIView):
	queryset = Hotel.objects.all()
	serializer_class = RegisterHotelSerializer

@permission_classes((CanEditBusinessObject,permissions.IsAuthenticated,))
class HotelPartialUpdateView(generics.GenericAPIView, UpdateModelMixin):
	queryset = Hotel.objects.all()
	serializer_class = RegisterHotelSerializer

	def post(self, request, *args, **kwargs):
		return self.partial_update(request, *args, **kwargs)


@api_view(["GET"])
def getAllTags(request):
	tags = Tag.objects.all()
	print(tags)
	serializer = TagsSerializer(tags, many=True)
	return Response(serializer.data)
