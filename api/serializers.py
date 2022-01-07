from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from api.models import Hotel, City, Country, User
from django.contrib.auth.password_validation import validate_password
import uuid
from taggit.serializers import TagListSerializerField, TaggitSerializer
from taggit.models import Tag
import json

class HotelsSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'tags', 'locLong', 'locLat', 'available', 'bookingLink', 'updated_on']

class HotelSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    ownedByName = serializers.CharField(source='ownedBy.full_name', default="")
    ownedByID = serializers.IntegerField(source='ownedBy.id', default=-1)
    class Meta:
        model = Hotel
        fields = ['name', 'tags', 'bookingLink', 'updated_on', 'isFetchedFromBooking', 'description', 'available', 'ownedByName', 'ownedByID', 'locLong', 'locLat']

class CitySerializer(serializers.ModelSerializer):
    countryName = serializers.CharField(source='country.name')
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'countryName']

class TagsSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Tag
		fields = ["name"]

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwags = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data, user=None):
        if user is None:
            username = str(uuid.uuid4()) # we do not need the username field, but django.contrib.auth requires it to exist and be unique so we are generating a random uuid for each user to handle that 
            user = User.objects.create(username=username, email=validated_data["email"],
            first_name=validated_data["first_name"], last_name=validated_data["last_name"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class BusinessRegisterSerializer(RegisterSerializer):
    def create(self, validated_data):
        username = str(uuid.uuid4())
        user = User.objects.create(username=username, email=validated_data["email"],
        first_name=validated_data["first_name"], last_name=validated_data["last_name"], isBusinessClient=True)
        user = super().create(validated_data, user)
        return user

class RegisterHotelSerializer(serializers.ModelSerializer):
	tags = TagListSerializerField()
	class Meta:
		model = Hotel
		fields = ['name', 'city', 'description', 'tags']

	def create(self, validated_data):
		user = None
		request = self.context.get('request')
		if request and hasattr(request, "user"):
			user = request.user

		hotel = Hotel.objects.create(name=validated_data["name"], city=validated_data["city"], description=validated_data["description"], ownedBy=user)
		
		hotel.tags.set(validated_data["tags"])
		hotel.save()
		return hotel

	
	def update(self, instance, validated_data):
		instance.name = validated_data["name"]
		instance.description = validated_data["description"]
		instance.city = validated_data["city"]
		instance.tags.set(validated_data["tags"])
		instance.save()
		return instance

