from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City, Restaurant, SearchPhrase
import requests
import json

class Command(BaseCommand):
    help = 'Migrates city names to SearchPhrases'

    def handle(self, *args, **options):
        for city in City.objects.all():
            created = SearchPhrase.objects.get_or_create(phrase=city.name, city=city)[1]
            if created is True:
                self.stdout.write(self.style.SUCCESS("Migrated city <id, name>: {}, {}".format(city.id, city.name)))
        self.stdout.write(self.style.SUCCESS("Completed Migration"))
