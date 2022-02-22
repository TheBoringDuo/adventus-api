from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City, Restaurant
import requests
import json

class Command(BaseCommand):
    help = 'Helps you add a country to the records'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs='?', type=str, default="Bulgaria")
        parser.add_argument('city', nargs='?', type=str, default="Varna")

    def handle(self, *args, **options):
        country = options['country']
        city = options['city']
        location = city + " " + country

        try:
            countryObj = Country.objects.get(name=country)
            try:
                cityObj = City.objects.get(name=city, country=countryObj)
            except Exception as e:
                print(e)
                return
        except Exception as e:
            print(e)
            return

        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', "X-Requested-By": "andsowesucceded"}
        s = requests.Session()
        r = s.get("http://www.tripadvisor.com", headers=headers)
        headersForAutoCompletion = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', "X-Requested-By": "andsowesucceded", 'Content-type': 'application/json', "Referer": "https://www.tripadvisor.com/"}

        print(r.text)
        parameters = ""
        url1 = 'https://www.tripadvisor.com/data/graphql/ids'
        postDATA = [
            {
                "query": "c9d791589f937ec371723f236edc7c6b",
                "variables":
                {
                    "request":
                    {
                        "query":location,
                        "limit":10,
                        "scope":"WORLDWIDE",
                        "locale":"en-US",
                        "scopeGeoId":1,
                        "searchCenter":None,
                        "types":
                        [
                            "LOCATION",
                            "RESCUE_RESULT"
                        ],
                        "locationTypes":["GEO","NEIGHBORHOOD"],
                        "userId":None
                    }
                }
            }
        ]
        print("here")
        print(s.cookies.get_dict())
        response = s.post('https://www.tripadvisor.com/data/graphql/ids', headers=headersForAutoCompletion, json=postDATA, timeout=5)

        print("here2")
        linkData = json.loads(response.text)
        print(linkData)
        restaurantsURL = linkData[0]["data"]["Typeahead_autocomplete"]["results"][0]["details"]["RESTAURANTS_URL"]
        print(linkData)
        print(restaurantsURL)
        page = s.get(('https://www.tripadvisor.com'+restaurantsURL), headers=headers)
        soup = BeautifulSoup(page.content, 'lxml')
        mainResDiv = soup.find('div', {"data-test-target": "restaurants-list"})
        with open('output.txt', 'w') as out:
            out.write(str(page.content))
        i = 0
        for item in mainResDiv.select('div[data-test*="list_item"]'):
            a = item.find('a', {"class": 'bHGqj Cj b'}) # not the best practice as the class names are automatically generated and can change
            # but there is nothing we can do about this as thjere is no other way
            try: # this part of the code will remove the sponsored restaurant
                int(a.contents[0])
            except:
                continue
            name = a.contents[-1]
            print(name)
            link = a["href"]
            print(link)
            restaurant, created = Restaurant.objects.get_or_create(city=cityObj, name=name)
            restaurant.tripadvisorLink = "https://www.tripadvisor.com" + link
            restaurant.save()

