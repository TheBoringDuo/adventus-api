import asyncio
from aiohttp import ClientSession
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City
#import spacy
import numpy as np
# from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import sys
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
import re

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

async def fetch(hotelobj, session):
    url = hotelobj["hotel_link"]
    hotel_id = hotelobj["hotel_id"]
    r = dict()
    print("Starting to fetch", hotel_id)
    async with session.get(url, headers=headers) as response:
        r['response'] = await response.text()
        print("Fetched", hotel_id)
        r['hotel_id'] = hotel_id
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


async def do_as_completed(hotels, hotelDescriptions, hotelIds):
    to_exclude = []
    loop = asyncio.get_event_loop()
    async with ClientSession() as session:
        
        tasks = [loop.create_task(fetch(hotelobj, session)) for hotelobj in hotels]
        async for future in as_completed_async(tasks):
            try:
                res = await future
            except Exception as e:
                res = e
        
            response = res['response']
            hotel_id = res['hotel_id']
 
            soup=BeautifulSoup(response, 'lxml')
            
            if soup.find('div', attrs = {'class': 'bui-empty-state'}): # Stop scraping when there are no more reviews
                to_exclude.append(hotel_id)
                print("Empty")

            for item in soup.find_all('div', attrs = {'class': 'c-review-block'}):
                title = ''
                positive = ''

                try:
                    itemSelected = item.find('h3', attrs = {'class': 'c-review-block__title'})
                    if itemSelected is not None:
                        title = itemSelected.text
                except Exception as e:
                    # raise e
                    print(e)

                try:
                    itemSelected = item.find('span', attrs= {'class': 'c-review__body'})
                    if itemSelected is not None:
                        positive = itemSelected.text
                except Exception as e:
                    print(e)

                hotelDescriptions[hotel_id] += title + " " + positive
            print("Done with", hotel_id)
        return hotelDescriptions, hotelIds, to_exclude

class Command(BaseCommand):
 
    help = 'Recommends the best hotel based on keywords, given by the user as input'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs='?', type=str, default="Bulgaria")
        parser.add_argument('city', nargs='?', type=str, default="Varna")
        parser.add_argument('keywords', nargs='?', type=str, default="")
        parser.add_argument('pages', nargs='?', type=int, default=1)

    def handle(self, *args, **options):
        country = options['country']
        city = options['city']
        keywords = options['keywords']
        pages = options['pages']
       
        
        loop = asyncio.get_event_loop()
        
        try:
            countryObj = Country.objects.get(name=country)
            try:
                cityObj = City.objects.get(name=city, country=countryObj)
            except Exception as e:
                print(e)
                self.stdout.write(self.style.ERROR("There is no record of such city"))
                return
        except Exception as e:
            print(e)
            self.stdout.write(self.style.ERROR("There is no record of such country"))
            return

        # self.stdout.write(self.style.SUCCESS("Scraping Booking.com for {}, {}".format(city, country)))

        hotels = Hotel.objects.filter(city=cityObj)
        hotelDescriptions = dict()
        hotelIds = []
        hotels = hotels.exclude(bookingLink=None)
        hotel_count = hotels.count()
        offset = 0
        
        while hotel_count > 0 and offset < pages*25:
            print("Count", hotel_count)
            hotelsobj = [] # need a separate hotelsobj to pass to the async function as django cannot handle working with models in async
            for hotel in hotels:
                if getattr(hotel, 'id') not in hotelIds:
                    hotelIds.append(getattr(hotel, 'id'))
                if getattr(hotel, 'id') not in hotelDescriptions:
                    hotelDescriptions[getattr(hotel, 'id')] = ''
                try:
                    url1 = 'https://www.booking.com/reviewlist.en-gb.html?cc1=' + (re.search(r'\/[A-Za-z]{2}\/(.*?)\.', getattr(hotel, 'bookingLink')).group(0))[1:3] + ';pagename=' + re.search(r'\/[A-Za-z]{2}\/(.*?)\.', getattr(hotel, 'bookingLink')).group(1) + ';type=total&;offset=' + str(offset) + ';rows=25#'
                    
                    # self.stdout.write(self.style.SUCCESS("URL found: {}".format(url1)))
                     
                    hotelobj = dict()
                    hotelobj["hotel_id"] = hotel.id
                    hotelobj["hotel_link"] = url1
                    hotelsobj.append(hotelobj)
                
                except Exception as e:
                    hotels = hotels.exclude(id=hotel.id)
            future = asyncio.ensure_future(do_as_completed(hotelsobj, hotelDescriptions, hotelIds))
            loop.run_until_complete(future)
            hotelDescriptions, hotelIds, to_exclude = future.result()
            hotels = hotels.exclude(id__in=to_exclude)  
            offset += 25
            hotel_count = hotels.count()

        
        descriptionsRaw = []
        for key in hotelDescriptions:
            descriptionsRaw.append(hotelDescriptions[key])

        countVectorizer = CountVectorizer()
        sparseMatrix = countVectorizer.fit_transform(descriptionsRaw)
        sparseMatrixKeywords = countVectorizer.transform([keywords])

        similarityRow = cosine_similarity(sparseMatrix, sparseMatrixKeywords)
        
        bestHotels = dict()
        for i in range(0, len(hotelIds)):
            bestHotels[hotelIds[i]] = similarityRow[i]

        for key in dict(sorted(bestHotels.items(), key=lambda item: item[1], reverse=True)):
            self.stdout.write(self.style.SUCCESS("Recommended Hotel: {}, {}".format(getattr( Hotel.objects.get(id=key), 'name' ), getattr( Hotel.objects.get(id=key), 'bookingLink' ))))
