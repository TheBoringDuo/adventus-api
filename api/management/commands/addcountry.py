from bs4 import BeautifulSoup
import requests
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City

class Command(BaseCommand):
    help = 'Helps you add a country to the records'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs='?', type=str, default="Bulgaria")

    def handle(self, *args, **options):
        country = options['country']
        
        try:
            Country.objects.create(name=country)
            self.stdout.write(self.style.SUCCESS("Added a record of a country {}".format(country)))
        except Exception as e:
            print(e)   
            self.stdout.write(self.style.ERROR("There is already a record of a country with that name"))
            return
