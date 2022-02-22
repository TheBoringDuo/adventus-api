from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City, Restaurant
import requests
import json


def findrestaurants(cityObj):
    location = cityObj.name + " " + cityObj.country.name

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', "X-Requested-By": "andsowesucceded"}
    s = requests.Session()
    r = s.get("http://www.tripadvisor.com", headers=headers)
    headersForAutoCompletion = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', "X-Requested-By": "andsowesucceded", 'Content-type': 'application/json', "Referer": "https://www.tripadvisor.com/"}

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

    response = s.post('https://www.tripadvisor.com/data/graphql/ids', headers=headersForAutoCompletion, json=postDATA, timeout=5)


    linkData = json.loads(response.text)

    restaurantsURL = linkData[0]["data"]["Typeahead_autocomplete"]["results"][0]["details"]["RESTAURANTS_URL"]

    page = s.get(('https://www.tripadvisor.com'+restaurantsURL), headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')
    mainResDiv = soup.find('div', {"data-test-target": "restaurants-list"})

    to_return = []

    for item in mainResDiv.select('div[data-test*="list_item"]'):
        a = item.find('a', {"class": 'bHGqj Cj b'}) # not the best practice as the class names are automatically generated and can change
        # but there is nothing we can do about this as thjere is no other way
        try: # this part of the code will remove the sponsored restaurant
            int(a.contents[0])
        except:
            continue
        name = a.contents[-1]
        link = a["href"]
        restaurant, created = Restaurant.objects.get_or_create(city=cityObj, name=name)
        restaurant.tripadvisorLink = "https://www.tripadvisor.com" + link
        restaurant.save()
        to_return.append(restaurant)
    return to_return