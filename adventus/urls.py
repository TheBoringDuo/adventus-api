"""tripplanning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import api.views as api
from django.conf import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get_hotels_by_city/<cityID>/', api.getHotelsByCityID),
    path('get_hotels_by_city/<cityID>/<limitResults>/', api.getHotelsByCityID),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get_cities/', api.getAllCitiesByCountryOrNot),
	path('register/', api.RegisterView.as_view(), name='auth_register'),
	path('register/business/', api.BusinessRegisterView.as_view(), name='auth_register_business'),
    path('test/', api.testView, name='testView'),
    path('get_hotel_by_id/<hotelID>/', api.getHotelByID),
    path('get_hotels_by_tags/<cityID>/', api.getHotelsByCityAndTags),
	path('register_hotel/', api.RegisterHotelView.as_view(), name='register_hotel'),
	path('tags/', api.getAllTags),
	path('update_hotel/<pk>/', api.HotelPartialUpdateView.as_view(), name='update_hotel'),
    path('get_restaurant_by_id/<restaurantID>/', api.getRestaurantByID),
    path('register_restaurant/', api.RegisterRestaurantView.as_view(), name='register_restaurant'),
    path('get_rests_by_city/<cityID>/', api.getRestaurantsByCityID),
    path('get_rests_by_city/<cityID>/<limitResults>/', api.getRestaurantsByCityID),
    path('update_restaurant/<pk>/', api.RestaurantPartialUpdateView.as_view(), name='update_rest'),
    path('get_rests_by_tags/<cityID>/', api.getRestaurantsByCityAndTags),
    path('link_restaurant/', api.connectRestaurantToHotel),
    path('findhotels/<countryName>/<cityName>/<keywords>/', api.getHotelsFromKeywords),
    path('findhotels/<countryName>/<cityName>/', api.getHotelsFromKeywords),
    path('findhotels/<countryName>/<cityName>//', api.getHotelsFromKeywords), # weird but necessary
    path('findrestaurants/<countryName>/<cityName>/<keywords>/', api.getRestaurantsFromKeywords),
    path('findrestaurants/<countryName>/<cityName>/', api.getRestaurantsFromKeywords),
    path('findrestaurants/<countryName>/<cityName>//', api.getRestaurantsFromKeywords), # weird but necessary
    path('add_to_favourites/', api.addToFavouriteHotels),
    path('remove_from_favourites/', api.removeFromFavouriteHotels),
    path('favourite_hotels/', api.getFavouriteHotels),
    path('get_restaurants/<countryName>/<cityName>/', api.getRestaurantsByNames),
    path('profile/', api.getProfile),
    path('api/password_reset/', include('django_rest_passwordreset.urls'))
]

if settings.DEBUG is False:
    urlpatterns.append(path('', api.indexInProd))