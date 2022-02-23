import requests
from bs4 import BeautifulSoup
import json

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}


def fetchByCityAndCountry(cityName, countryName):
    s = requests.Session()
    response = s.get("https://www.booking.com/", headers=headers)
    soup=BeautifulSoup(response.content,'lxml').prettify()
    csrfToken = str(soup).split("'X-Booking-CSRF': '", 1)[1].split("'",1)[0]

    headers["X-Booking-Csrf"] = csrfToken
    headers["X-Booking-Client-Info"] = "wqhje213213jhk123h"

    url = "https://www.booking.com/autocomplete_csrf?v=1&lang=en-us&aid=eedwqe&pid=ku123dd213&term=" + cityName + ",%20" + countryName
    if countryName.lower() == "customsearch": # Allows for requests where we can't find the country in the list of countries
        url = "https://www.booking.com/autocomplete_csrf?v=1&lang=en-us&aid=eedwqe&pid=ku123dd213&term=" + cityName

    response2 = s.get(url, headers=headers)

    response_json = json.loads(response2.content)
   
    try:
        destID = response_json['city'][0]['dest_id']
    except:
        destID = None
    return destID 
    

