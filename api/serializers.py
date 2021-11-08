from rest_framework import serializers
from api.models import Hotel, City, Country


class HotelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'link', 'updated_on']

class CitySerializer(serializers.ModelSerializer):
    countryName = serializers.CharField(source='country.name')
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'countryName']
