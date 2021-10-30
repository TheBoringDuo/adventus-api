from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=30, unique=True)

class City(models.Model):
    name = models.CharField(max_length=30)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)
    destID = models.CharField(max_length=12, unique=True, null=False)
    
    class Meta:
        unique_together = ('name', 'country')

class Hotel(models.Model):
    name = models.CharField(max_length=50)
    link = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

