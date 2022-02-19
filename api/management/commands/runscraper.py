from bs4 import BeautifulSoup
import requests
from django.core.management.base import BaseCommand, CommandError
from api.models import Hotel, Country, City

class Command(BaseCommand):
    help = 'Scrapes Booking.com to find all of the hotels from a certain city'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs='?', type=str, default="Bulgaria")
        parser.add_argument('city', nargs='?', type=str, default="Varna")
        parser.add_argument('unlimited', nargs='?', type=bool, default=False) # Setting the 'unlimited' argument to true runs the scraper for every hotel, not just the top rated ones; however this is very resource intensive and takes a lot of time, so by default we're only taking the best 25 ones according to Booking users

    def handle(self, *args, **options):
        country = options['country']
        city = options['city']
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

        self.stdout.write(self.style.SUCCESS("Scraping Booking.com for {}, {}".format(city, country)))
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

        destID = cityObj.destID 

        allFetched = []
        repeated = []
        i = 1
        cont = True
        offset = 0
        while cont:
            url1 = 'https://www.booking.com/searchresults.html?dest_id=' + destID + '&dest_type=city&offset=' + str(offset)
            response=requests.get(url1,headers=headers)

            soup=BeautifulSoup(response.content,'lxml')
            cont = False
            for item in soup.find_all('div', attrs = {'data-testid': 'property-card'}):
                try:
                    hotelName = item.find('div', attrs = {'data-testid': 'title'}).string    
                    link = item.find('a', attrs = {'data-testid': 'title-link'})["href"]
                    cont = options['unlimited'] # False by default to stop the loop at 25
                    linkPic = item.find('img', attrs={'data-testid': 'image'})["src"]
                    print(linkPic)
                    reviewStatus = item.find('div', attrs = {'data-testid': 'review-score'})
                    element = reviewStatus.select('div[aria-label*="Scored"]')[0]
                    rating = float(element['aria-label'].split(" ")[1])
                        
                    starRatingDiv = item.find('div', attrs={'data-testid': 'rating-stars'})
                    if starRatingDiv is not None:
                        starRating = len(starRatingDiv.find_all('span'))
                    
                    hotel, created = Hotel.objects.get_or_create(city=cityObj, name=hotelName)
                    hotel.bookingLink = link
                    hotel.linkToBookingPic = linkPic
                    hotel.bookingRating = rating
                    hotel.starRating = starRating
                    hotel.save()

                    if hotelName not in allFetched:
                        allFetched.append(hotelName)
                    else:
                        repeated.append(hotelName)
                except Exception as e:
                    #raise e
                    print(e)
                    print('')
                i += 1 # TODO: Explain why is this i even here
            offset += 25
        self.stdout.write(self.style.SUCCESS("Totally scraped {} hotels!".format(len(allFetched))))
