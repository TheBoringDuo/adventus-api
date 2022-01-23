from bs4 import BeautifulSoup
import requests

from requests_threads import AsyncSession
import re
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City
#import spacy
import numpy as np
# from sklearn.feature_extraction import text
from sklearn.feature_extraction.text import CountVectorizer
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react


class Command(BaseCommand):
	help = 'Recommends the best hotel based on keywords, given by the user as input'

	def add_arguments(self, parser):
		parser.add_argument('country', nargs='?', type=str, default="Bulgaria")
		parser.add_argument('city', nargs='?', type=str, default="Varna")
		parser.add_argument('keywords', nargs='?', type=str, default="")
		parser.add_argument('pages', nargs='?', type=int, default=1)

	@inlineCallbacks
	def handle_real(self, *args, **options):
		country = self.country
		city = self.city
		keywords = self.keywords
		pages = self.pages
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
		hotels = hotels.exclude(bookingLink=None)
		hotel_count = hotels.count()
		print(hotel_count)

		offset = 0
		while hotel_count > 0 and offset<pages*25:
			responses = []
			session = AsyncSession(n=hotel_count)
			for hotel in hotels:
				
				if getattr(hotel, 'id') not in hotelIds:
					hotelIds.append(getattr(hotel, 'id'))
				if getattr(hotel, 'id') not in hotelDescriptions:
					hotelDescriptions[getattr(hotel, 'id')] = ''
				try:
					url1 = 'https://www.booking.com/reviewlist.en-gb.html?cc1=bg;pagename=' + re.search(r'\/bg\/(.*?)\.', getattr(hotel, 'bookingLink')).group(1) + ';type=total&;offset=' + str(offset) + ';rows=25#';
					url12 = 'https://www.booking.com/reviewlist.en-gb.html?cc1=' + (re.search(r'\/[A-Za-z]{2}\/(.*?)\.', getattr(hotel, 'bookingLink')).group(0))[1:3] + ';pagename=' + re.search(r'\/[A-Za-z]{2}\/(.*?)\.', getattr(hotel, 'bookingLink')).group(1) + ';type=total&;offset=' + str(offset) + ';rows=25#'
					
					# self.stdout.write(self.style.SUCCESS("URL found: {}".format(url1)))
					responses.append({"hotel": hotel, "response": session.get(url1,headers=headers)})
				   
				except:
					hotels = hotels.exclude(id=hotel.id)
			
		
			for response in responses:
				r = response["response"]
				hotel = response["hotel"]
				print(hotel)
				response = yield r
				soup=BeautifulSoup(response.content,'lxml')

				if soup.find('div', attrs = {'class': 'bui-empty-state'}): # Stop scraping when there are no more reviews
					hotels = hotels.exclude(id=hotel.id)
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

					hotelDescriptions[getattr(hotel, 'id')] += title + " " + positive
			offset += 25
			hotel_count = hotels.count()
	
		
		#print(hotelDescriptions)
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
		
	def handle(self, *args, **options):
		self.country = options["country"]
		self.city = options["city"]
		self.keywords = options["keywords"]
		self.pages = options["pages"]
		react(self.handle_real)
