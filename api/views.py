from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import authentication, permissions, generics
# Create your views here.
from api.models import Hotel, City, Country, User, Restaurant
from api.serializers import HotelsSerializer, CitySerializer, RegisterSerializer, BusinessRegisterSerializer, HotelSerializer, RestaurantSerializer, RestaurantsSerializer, RegisterRestaurantSerializer
from api.serializers import RegisterHotelSerializer, TagsSerializer, LinkRestaurantToHotelSerializer
from django.http import HttpResponse
from .permissions import CanAddBusinessObjects, CanEditBusinessObject
from taggit.models import Tag
from rest_framework.mixins import UpdateModelMixin
from api.supportFunctions.findhotel import findHotel
from api.supportFunctions.runscraper import runScraper
from api.supportFunctions.fetchIDFunctions import fetchByCityAndCountry
import json

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
# @permission_classes((permissions.IsAuthenticated,))
def getRestaurantsByCityID(request, cityID, limitResults = -1):
    try:
        if limitResults == -1:
            restaurants = Restaurant.objects.filter(city__id = cityID, active=True, listed=True)
        else:
            restaurants = Restaurant.objects.filter(city__id = cityID, pk__lte = limitResults, active=True, listed=True)
    except Exception as e:
        print(e)
        return Response("{}")

    serializer = RestaurantsSerializer(restaurants, many=True)

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
def getRestaurantByID(request, restaurantID):
    try:
        restaurant = Restaurant.objects.get(id=restaurantID, active=True)
        print(restaurant)
    except Exception as e:
        print(e)
        return Response("{}")

    serializer = RestaurantSerializer(restaurant)
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

@api_view(["GET"])
def getRestaurantsByCityAndTags(request, cityID):
    tags = request.GET.get('tags', None)
    if tags is None:
        return Response("{}")
    else:
        tags = tags.split(',')
        restaurants = Restaurant.objects.filter(city__id=cityID, tags__name__in=tags, active=True).distinct()
        if restaurants is not None:
            serializer = RestaurantsSerializer(restaurants, many=True)
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

@permission_classes((CanEditBusinessObject,permissions.IsAuthenticated,))
class RestaurantPartialUpdateView(generics.GenericAPIView, UpdateModelMixin):
    queryset = Restaurant.objects.all()
    serializer_class = RegisterRestaurantSerializer

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@permission_classes((CanAddBusinessObjects, permissions.IsAuthenticated,))
class RegisterRestaurantView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RegisterRestaurantSerializer

@api_view(["GET"])
def getAllTags(request):
	tags = Tag.objects.all()
	print(tags)
	serializer = TagsSerializer(tags, many=True)
	return Response(serializer.data)


@api_view(["POST"])
@permission_classes((CanAddBusinessObjects, permissions.IsAuthenticated,))
def connectRestaurantToHotel(request):
    serializer = LinkRestaurantToHotelSerializer(request.data)
    user = request.user
    hotel_id = serializer.data["hotel_id"]
    restaurant_id = serializer.data["restaurant_id"]
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except:
        return Response("Hotel with the given ID not found", status=418)

    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)
    except:
        return Response("Restaurant with the given ID not found", status=419)

    if hotel.ownedBy == user and restaurant.ownedBy == user:

        if hotel.restaurant == None and Hotel.objects.filter(restaurant__id=restaurant_id).count() == 0:
            hotel.restaurant = restaurant
            hotel.save()
            restaurant.locLong = hotel.locLong
            restaurant.locLat = hotel.locLat
            restaurant.save()
            return Response("Linked the restaurant to the hotel")
        else:
            return Response("There is already a restaurant linked to that hotel or the restaurant is linked to another hotel", status=420)
    else:
        return Response("You do not own the restaurant and/or the hotel", status=403)

    return Response("{}") 



@api_view(["GET"])
def getHotelsFromKeywords(request, countryName, cityName, keywords):
    cityExists = True
    try:
        countryObj = Country.objects.get(name__iexact=countryName)
        try:
            cityObj = City.objects.get(name__iexact=cityName, country=countryObj)
        except Exception as e:
            print(e)
            cityObj = City.objects.create(name=cityName, country=countryObj)
            bookingID = fetchByCityAndCountry(cityName, countryName)
            if bookingID is None:
                cityObj.delete()
                return Response("There is no such city", status=418)
            cityObj.destID = bookingID
            cityObj.save()

    except Exception as e:
        print(e)
        # if the country doesn't exist do not continue - we will add rows for every country
        # if we let the user add countries by creating a entry for each new one we will get ...

        return Response("There is no such country", status=418)

    ret = findHotel(cityObj, keywords, 2)
    if ret == 47:
        runScraper(cityObj, False) # unlimited = False for obvious reasons
        ret = findHotel(cityObj, keywords, 2)
        serializer = HotelsSerializer(ret, many=True)
        return Response(serializer.data)
    else:
        serializer = HotelsSerializer(ret, many=True)
        return Response(serializer.data)
        return Response(ret)
