from bs4 import BeautifulSoup
import requests
import re
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City
#import spacy
import numpy as np
# from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

class Command(BaseCommand):
    help = 'Recommends the best hotel based on keywords, given by the user as input'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs='?', type=str, default="Bulgaria")
        parser.add_argument('city', nargs='?', type=str, default="Varna")
        parser.add_argument('keywords', nargs='?', type=str, default="")

    def handle(self, *args, **options):
        country = options['country']
        city = options['city']
        keywords = options['keywords']
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
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

        hotels = Hotel.objects.filter(city=cityObj)
        hotelDescriptions = dict()
        hotelIds = []

        for hotel in hotels:
            offset = 0
            try:
                hotelIds.append(getattr(hotel, 'id'))
                hotelDescriptions[getattr(hotel, 'id')] = '' # TODO: In the local prototype with RapidAPI I also added the actual listing description, not just the reviews
                while True:
                    url1 = 'https://www.booking.com/reviewlist.en-gb.html?cc1=bg;pagename=' + re.search(r'\/bg\/(.*?)\.', getattr(hotel, 'bookingLink')).group(1) + ';type=total&;offset=' + str(offset) + ';rows=25#';
                    # self.stdout.write(self.style.SUCCESS("URL found: {}".format(url1)))

                    response=requests.get(url1,headers=headers)
                    soup=BeautifulSoup(response.content,'lxml')

                    if soup.find('div', attrs = {'class': 'bui-empty-state'}): # Stop scraping when there are no more reviews
                        break

                    for item in soup.find_all('div', attrs = {'class': 'c-review-block'}):
                        title = ''
                        positive = ''

                        try:
                            itemSelected = item.find('h3', attrs = {'class': 'c-review-block__title--original'})
                            if itemSelected is not None:
                                title = itemSelected.text
                        except Exception as e:
                            # raise e
                            print(e)

                        try:
                            itemSelected = item.find('span', attrs= {'class': 'c-review__body--original'})
                            if itemSelected is not None:
                                positive = itemSelected.text
                        except Exception as e:
                            print(e)

                        hotelDescriptions[getattr(hotel, 'id')] += title + " " + positive
                    offset += 25
            except Exception as e:
                # URL is probably not matching the format expected
                print(e)
                print('')

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

