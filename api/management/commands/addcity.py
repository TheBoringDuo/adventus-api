from bs4 import BeautifulSoup
import requests
import json
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
                    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

                    s = requests.Session()
                    response = s.get("https://www.booking.com/", headers=headers)
                    soup=BeautifulSoup(response.content,'lxml').prettify()
                    csrfToken = str(soup).split("'X-Booking-CSRF': '", 1)[1].split("'",1)[0]

                    headers["X-Booking-Csrf"] = csrfToken
                    headers["X-Booking-Client-Info"] = "wqhje213213jhk123hRandomshit"

                    url = "https://www.booking.com/autocomplete_csrf?v=1&lang=en-us&aid=eedwqe&pid=ku123dd213&term=" + city + ",%20" + country
                    response2 = s.get(url, headers=headers)

                    response_json = json.loads(response2.content)
                    print(response_json['city'][0]['city_name'])
                    destID = response_json['city'][0]['dest_id']

                City.objects.create(name=city, country=countryObj, destID=destID)
                self.stdout.write(self.style.SUCCESS("Added a record of a city {} in {} with Destionation ID {}".format(city, country, destID)))
            except Exception as e:
                print(e)   
                self.stdout.write(self.style.ERROR("There is already a record of a city with these parameters"))
                return
