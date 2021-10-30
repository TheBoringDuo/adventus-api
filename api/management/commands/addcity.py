from bs4 import BeautifulSoup
import requests
import json
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City
from api.supportFunctions.fetchIDFunctions import fetchByCityAndCountry

class Command(BaseCommand):
    help = 'Helps you add a city to the records'
    def add_arguments(self, parser):
        parser.add_argument('city', nargs='?', type=str, default="")
        parser.add_argument('country', nargs='?', type=str, default="")
        parser.add_argument('destID', nargs='?', type=str, default="")

    def handle(self, *args, **options):
        country = options['country']
        city = options['city']
        destID = options['destID']

        # make destID optional but still keep the option to
        # set it manually
        if country == "" or city == "": # or destID == "":
            self.stdout.write(self.style.ERROR("Not enough parameters passed"))
            return
        else:    
            try:
                try:
                    countryObj = Country.objects.get(name=country)
                except:
                    self.stdout.write(self.style.ERROR("There is no record of such country"))
                    return
                if destID == "":
                   destID = fetchByCityAndCountry(city, country)
                try:
                    City.objects.create(name=city, country=countryObj, destID=destID)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(e))
                    return
                self.stdout.write(self.style.SUCCESS("Added a record of a city {} in {} with Destionation ID {}".format(city, country, destID)))
            except Exception as e:
                print(e)   
                self.stdout.write(self.style.ERROR("There is already a record of a city with these parameters"))
                return
