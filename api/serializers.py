from rest_framework import serializers
from api.models import Hotel


class HotelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'link', 'updated_on']

