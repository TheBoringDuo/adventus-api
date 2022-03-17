from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City, Restaurant
import requests
import asyncio
import json
import numpy as np
import time
from aiohttp import ClientSession
import aiohttp
# from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import csv
import requests
import re
import time
import subprocess
import base64
from datetime import date, datetime, timedelta
from django.conf import settings
from django.utils import timezone


getlistLoc = "api/supportFunctions/goexecs/getlist"
getreviewsLoc = "api/supportFunctions/goexecs/getreviews"
geturlsLoc = "api/supportFunctions/goexecs/geturls"

def findrestaurantsGo(cityObj):
    if cityObj.country.name.lower() == "customsearch":
        location = cityObj.name
    else:
        location = cityObj.name + " " + cityObj.country.name

    result = subprocess.run([geturlsLoc, location], stdout=subprocess.PIPE).stdout
    linkData = json.loads(result)
    restaurantsURL = linkData[0]["data"]["Typeahead_autocomplete"]["results"][0]["details"]["RESTAURANTS_URL"]
    
    result = subprocess.run([getlistLoc, restaurantsURL], stdout=subprocess.PIPE).stdout
    soup = BeautifulSoup(result, 'lxml')

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



def findRestaurantsFromKeywordsGo(cityObj, keywords):
    restaurants = Restaurant.objects.filter(city=cityObj)
    if len(restaurants) == 0:
        return 47 # a random status code I made up on the spot - get bent
    restaurantDescription = dict()
    restaurantIds = []
    restaurants = restaurants.exclude(tripadvisorLink=None)
    restaurant_count = restaurants.count()
    offset = 0
    current_date = timezone.now()
    pastdate = current_date - settings.RESTAURANT_REVIEW_LIFETIME
    print(pastdate)
    cachedRestaurants = restaurants.filter(lastFetchedReviews__range=(pastdate, timezone.now())) # don't change timezone.now() to current_date here!!!!!!!!!!!
    cachedRestaurantIDs = cachedRestaurants.values('id')
    restaurants = restaurants.exclude(id__in=cachedRestaurantIDs)
    print("Count", restaurant_count)
    restaurantsobj = [] # need a separate hotelsobj to pass to the async function as django cannot handle working with models in async
    for restaurant in restaurants:
        if getattr(restaurant, 'id') not in restaurantIds:
            restaurantIds.append(getattr(restaurant, 'id'))
        if getattr(restaurant, 'id') not in restaurantDescription:
            restaurantDescription[getattr(restaurant, 'id')] = ''

        try:
            url = getattr(restaurant, 'tripadvisorLink')
            if offset != 0:
                urlArray = url.split('-Reviews-')
                url = urlArray[0] + '-Reviews-or' + offset + urlArray[1]
            restaurantObj = dict()
            restaurantObj["id"] = restaurant.id
            restaurantObj["url"] = url
            restaurantsobj.append(restaurantObj)
        except:
            restaurants = restaurants.exclude(id=restaurant.id)

    ## send restaurantsobj to getreviews
    restaurantPics = dict()
    if len(restaurantsobj) > 0:
        result = subprocess.run([getreviewsLoc, json.dumps(restaurantsobj)], stdout=subprocess.PIPE).stdout

        results = json.loads(result)
        for restaurant in results:
            output = base64.b64decode(restaurant['content'])
            soup=BeautifulSoup(output, 'lxml')
            base = soup.find_all("div", class_="listContainer")[0]

            try:
                picLink = soup.find("img", {"class": "basicImg"})["data-lazyurl"]
                restaurantPics[restaurant['id']] = picLink
            except Exception as e:
                print(e)
                pass
            for item in base.find_all("div", {"class": "reviewSelector"}):
                title = ''
                positive = ''

                try:
                    itemSelected = item.find('a', {"class": "title"}).select_one("span")
                    if itemSelected is not None:
                        title = itemSelected.text
                except Exception as e:
                    # raise e
                    print(e)

                try:
                    itemSelected = item.find("p", {"class": "partial_entry"})
                    if itemSelected is not None:
                        positive = itemSelected.text
                except Exception as e:
                    print(e)

                restaurantDescription[restaurant['id']] += title + " " + positive
    restaurant_count = restaurants.count()

    for restaurant in restaurants:
        try:
            desc = restaurantDescription[restaurant.id]
            print("Saving reviews for restaurant", restaurant.id)
            restaurant.reviews = desc
            try:
                picLink = restaurantPics[restaurant.id]
                restaurant.linkToTripadvisorPic = picLink
            except Exception as e:
                print(e)
            restaurant.lastFetchedReviews = timezone.now()
            restaurant.save()
        except Exception as e: #description doesn't exist continue
            print(e)
            pass
        
    for restaurant in cachedRestaurants:
        restaurantDescription[restaurant.id] = restaurant.reviews
        restaurantIds.append(restaurant.id)

    
    descriptionsRaw = []
    for key in restaurantDescription:
        descriptionsRaw.append(restaurantDescription[key])

    countVectorizer = CountVectorizer()
    sparseMatrix = countVectorizer.fit_transform(descriptionsRaw)
    sparseMatrixKeywords = countVectorizer.transform([keywords])
    similarityRow = cosine_similarity(sparseMatrix, sparseMatrixKeywords)
    bestRestaurants = dict()
    for i in range(0, len(restaurantIds)):
        bestRestaurants[restaurantIds[i]] = similarityRow[i]

    print(dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)))
    restaurants = []
    for key in dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)):
        ret = dict()
        restaurant = Restaurant.objects.get(id=key)
        restaurants.append(restaurant)
        # self.stdout.write(self.style.SUCCESS("Recommended Hotel: {}, {}".format(getattr( Hotel.objects.get(id=key), 'name' ), getattr( Hotel.objects.get(id=key), 'bookingLink' ))))

    print("here")
    return restaurants


def findrestaurants(cityObj):
    if cityObj.country.name.lower() == "customsearch":
        location = cityObj.name
    else:
        location = cityObj.name + " " + cityObj.country.name

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    s = requests.Session()
    r = s.get("https://www.tripadvisor.com/", headers=headers)
    headersForAutoCompletion = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', "X-Requested-By": "andsowesucceded", 'Content-type': 'application/json', "Referer": "https://www.tripadvisor.com/"}
    r.text
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
    print("sending r")

    response = s.post('https://www.tripadvisor.com/data/graphql/ids', headers=headersForAutoCompletion, json=postDATA, timeout=5)
    print("got response")

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

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36', 'Referer': 'https://www.tripadvisor.com/'}
async def fetch(restaurantobj, session):
    url = restaurantobj["restaurant_link"]
    print(url)
    restaurant_id = restaurantobj["restaurant_id"]
    r = dict()
    print("Starting to fetch", restaurant_id)
    async with session.get(url, headers=headers) as response:
        print("y", restaurant_id)
        r['response'] = await response.text()
        print("Fetched", restaurant_id)
        r['restaurant_id'] = restaurant_id
        return r

async def as_completed_async(futures):
    loop = asyncio.get_event_loop()
    wrappers = []
    for fut in futures:
        assert isinstance(fut, asyncio.Future)  # we need Future or Task
        # Wrap the future in one that completes when the original does,
        # and whose result is the original future object.
        wrapper = loop.create_future()
        fut.add_done_callback(wrapper.set_result)
        wrappers.append(wrapper)
    for next_completed in asyncio.as_completed(wrappers):
        # awaiting next_completed will dereference the wrapper and get
        # the original future (which we know has completed), so we can
        # just yield that
        yield await next_completed


async def do_as_completed(restaurants, restaurantDescription, restaurantIds):
    to_exclude = []
    loop = asyncio.get_event_loop()
    async with ClientSession() as session:
        print(session)
        tasks = [loop.create_task(fetch(restaurantobj, session)) for restaurantobj in restaurants]
        async for future in as_completed_async(tasks):
            try:
                res = await future
            except Exception as e:
                res = e
        
            response = res['response']
            restaurant_id = res['restaurant_id']
 
            soup=BeautifulSoup(response, 'lxml')
            base = soup.find_all("div", class_="listContainer")[0]

            for item in base.find_all("div", {"class": "reviewSelector"}):
                title = ''
                positive = ''

                try:
                    itemSelected = item.find('a', {"class": "title"}).select_one("span")
                    if itemSelected is not None:
                        title = itemSelected.text
                except Exception as e:
                    # raise e
                    print(e)

                try:
                    itemSelected = item.find("p", {"class": "partial_entry"})
                    if itemSelected is not None:
                        positive = itemSelected.text
                except Exception as e:
                    print(e)

                restaurantDescription[restaurant_id] += title + " " + positive
            print("Done with", restaurant_id)
        return restaurantDescription, restaurantIds, to_exclude


def findRestaurantsFromKeywords(cityObj, keywords, pages):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)    
    restaurants = Restaurant.objects.filter(city=cityObj)
    if len(restaurants) == 0:
        return 47 # a random status code I made up on the spot - get bent
    restaurantDescription = dict()
    restaurantIds = []
    restaurants = restaurants.exclude(tripadvisorLink=None)
    restaurant_count = restaurants.count()
    offset = 0
    while restaurant_count > 0 and offset < pages*15:
        print("Count", restaurant_count)
        restaurantsobj = [] # need a separate hotelsobj to pass to the async function as django cannot handle working with models in async
        for restaurant in restaurants:
            if getattr(restaurant, 'id') not in restaurantIds:
                restaurantIds.append(getattr(restaurant, 'id'))
            if getattr(restaurant, 'id') not in restaurantDescription:
                restaurantDescription[getattr(restaurant, 'id')] = ''

            try:
                url = getattr(restaurant, 'tripadvisorLink')
                if offset != 0:
                    urlArray = url.split('-Reviews-')
                    url = urlArray[0] + '-Reviews-or' + offset + urlArray[1]
                restaurantObj = dict()
                restaurantObj["restaurant_id"] = restaurant.id
                restaurantObj["restaurant_link"] = url
                restaurantsobj.append(restaurantObj)
            except:
                restaurants = restaurants.exclude(id=restaurant.id)
        future = asyncio.ensure_future(do_as_completed(restaurantsobj, restaurantDescription, restaurantIds))
        loop.run_until_complete(future)
        restaurantDescription, restaurantIds, to_exclude = future.result()
        restaurants = restaurants.exclude(id__in=to_exclude)  
        offset += 15
        restaurant_count = restaurants.count()
        descriptionsRaw = []
        for key in restaurantDescription:
            descriptionsRaw.append(restaurantDescription[key])

        countVectorizer = CountVectorizer()
        sparseMatrix = countVectorizer.fit_transform(descriptionsRaw)
        sparseMatrixKeywords = countVectorizer.transform([keywords])
        similarityRow = cosine_similarity(sparseMatrix, sparseMatrixKeywords)
        bestRestaurants = dict()
        for i in range(0, len(restaurantIds)):
            bestRestaurants[restaurantIds[i]] = similarityRow[i]

        print(dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)))
        restaurants = []
        for key in dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)):
            ret = dict()
            restaurant = Restaurant.objects.get(id=key)
            restaurants.append(restaurant)
            # self.stdout.write(self.style.SUCCESS("Recommended Hotel: {}, {}".format(getattr( Hotel.objects.get(id=key), 'name' ), getattr( Hotel.objects.get(id=key), 'bookingLink' ))))

        print("here")
        return restaurants

    

def findRestaurantsFromKeywordsSync(cityObj, keywords, pages):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    restaurants = Restaurant.objects.filter(city=cityObj)
    if len(restaurants) == 0:
        return 47 # a random status code I made up on the spot - get bent
    restaurantDescription = dict()
    restaurantIds = []
    restaurants = restaurants.exclude(tripadvisorLink=None)
    restaurant_count = restaurants.count()
    offset = 0
    while restaurant_count > 0 and offset < pages*15:
        print("Count", restaurant_count)
        for count, restaurant in enumerate(restaurants):
            if count > 15:
                break
            if getattr(restaurant, 'id') not in restaurantIds:
                restaurantIds.append(getattr(restaurant, 'id'))
            if getattr(restaurant, 'id') not in restaurantDescription:
                restaurantDescription[getattr(restaurant, 'id')] = ''
            link = restaurant.tripadvisorLink
            r = requests.get(link, headers=headers)
            soup=BeautifulSoup(r.content, 'lxml')

            picLink = soup.find("img", {"class": "basicImg"})["data-lazyurl"]
            restaurant.linkToTripadvisorPic = picLink

            restaurant.save()

            base = soup.find_all("div", class_="listContainer")[0]

            for item in base.find_all("div", {"class": "reviewSelector"}):
                title = ''
                positive = ''

                try:
                    itemSelected = item.find('a', {"class": "title"}).select_one("span")
                    if itemSelected is not None:
                        title = itemSelected.text
                except Exception as e:
                    # raise e
                    print(e)

                try:
                    itemSelected = item.find("p", {"class": "partial_entry"})
                    if itemSelected is not None:
                        positive = itemSelected.text
                except Exception as e:
                    print(e)

                
                restaurantDescription[restaurant.id] += title + " " + positive
            print("Done with", restaurant.id)

        offset += 15
        restaurant_count = restaurants.count()
        descriptionsRaw = []
        for key in restaurantDescription:
            descriptionsRaw.append(restaurantDescription[key])

        countVectorizer = CountVectorizer()
        sparseMatrix = countVectorizer.fit_transform(descriptionsRaw)
        sparseMatrixKeywords = countVectorizer.transform([keywords])
        similarityRow = cosine_similarity(sparseMatrix, sparseMatrixKeywords)
        bestRestaurants = dict()
        for i in range(0, len(restaurantIds)):
            bestRestaurants[restaurantIds[i]] = similarityRow[i]

        print(dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)))
        restaurants = []
        for key in dict(sorted(bestRestaurants.items(), key=lambda item: item[1], reverse=True)):
            ret = dict()
            restaurant = Restaurant.objects.get(id=key)
            restaurants.append(restaurant)
            # self.stdout.write(self.style.SUCCESS("Recommended Hotel: {}, {}".format(getattr( Hotel.objects.get(id=key), 'name' ), getattr( Hotel.objects.get(id=key), 'bookingLink' ))))

        print("here")
        return restaurants
