from unicodedata import decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
import django.contrib.auth.models as authModels
from taggit.managers import TaggableManager
# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=30, unique=True)

class City(models.Model):
    name = models.CharField(max_length=30)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    destID = models.CharField(max_length=12, unique=True, null=False)
    
    def __str__(self):
        return "{}, {}".format(self.name, self.country.name)

    class Meta:
        unique_together = ('name', 'country')
    

class User(AbstractUser):
    email = models.EmailField(unique=True)
    isBusinessClient = models.BooleanField(default=False)
    favouriteHotels = models.ManyToManyField('Hotel', default=None)
    
    USERNAME_FIELD = AbstractUser.get_email_field_name()
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    

class Restaurant(models.Model):
    name = models.CharField(max_length=50)
    added_on = models.DateTimeField(auto_now_add=True)
    tripadvisorLink = models.TextField(default="")
    updated_on = models.DateTimeField(auto_now=True)
    isFetchedFromTripadvisor = models.BooleanField(default=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    description = models.TextField()
    available = models.BooleanField(default=True) # a field that the business clients can edit - if false, it will be listed at the bottom
    #but won't be used by adventus for suggestions and planning because it means the hotel isn't available at the moment
    active = models.BooleanField(default=True) # a field that the admins can edit - if false, it won't be listed anywhere on the platform
    listed = models.BooleanField(default=True) # a field that the business clients can edit - if false, it won't be listed anywhere on the platform
    ownedBy = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    locLong = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    locLat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    tags = TaggableManager()

class Hotel(models.Model):
    name = models.CharField(max_length=50)
    bookingLink = models.TextField(default="")
    linkToBookingPic = models.TextField(default="", null=True)
    starRating = models.IntegerField(default=None, null=True)
    bookingRating = models.DecimalField(default=None, null=True, decimal_places=1, max_digits=2)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    isFetchedFromBooking = models.BooleanField(default=True)
    description = models.TextField(default="")
    available = models.BooleanField(default=True) # a field that the business clients can edit - if false, it will be listed at the bottom
    #but won't be used by adventus for suggestions and planning because it means the hotel isn't available at the moment
    active = models.BooleanField(default=True) # a field that the admins can edit - if false, it won't be listed anywhere on the platform
    listed = models.BooleanField(default=True) # a field that the business clients can edit - if false, it won't be listed anywhere on the platform
    ownedBy = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    locLong = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    locLat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    tags = TaggableManager()
    restaurant = models.OneToOneField(Restaurant, on_delete=models.DO_NOTHING, null=True)
    
