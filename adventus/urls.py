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
from django.urls import path
import api.views as api

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get_by_city_id/<cityID>/', api.getHotelsByCityID),
    path('get_by_city_id/<cityID>/<limitResults>/', api.getHotelsByCityID),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get_cities/', api.getAllCitiesByCountryOrNot),
	path('register/', api.RegisterView.as_view(), name='auth_register'),
	path('register/business/', api.BusinessRegisterView.as_view(), name='auth_register_business'),
    path('test/', api.testView, name='testView'),
    path('get_hotel_by_id/<hotelID>/', api.getHotelByID)
]

