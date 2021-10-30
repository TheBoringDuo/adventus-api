from bs4 import BeautifulSoup
import requests
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City

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

        if country == "" or city == "" or destID == "":
            self.stdout.write(self.style.ERROR("Not enough parameters passed"))
            return
        else:    
            try:
                try:
                    countryObj = Country.objects.get(name=country)
                except:
                    self.stdout.write(self.style.ERROR("There is no record of such country"))
                    return
                City.objects.create(name=city, country=countryObj, destID=destID)
                self.stdout.write(self.style.SUCCESS("Added a record of a city {} in {} with Destionation ID {}".format(city, country, destID)))
            except Exception as e:
                print(e)   
                self.stdout.write(self.style.ERROR("There is already a record of a city with these parameters"))
                return
