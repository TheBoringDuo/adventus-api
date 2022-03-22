import requests
from bs4 import BeautifulSoup
import json
import redis
import time

redisClient = redis.Redis(host = '0.0.0.0', port=6379, db=0)
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
csrfToken = None
s = requests.Session()


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
    



def fetchByCityAssured(cityName): # this function's improvements is that is assures that a certain phrase is looked up only once and the other workers just wait

    lookupState = redisClient.get(cityName)
    channelClient = redisClient.pubsub()
    channelClient.subscribe(cityName)
    if lookupState is not None: # if not none something is already handling it
        print("Something is aleady handling it or is already handled")
        if lookupState != b'\0\0': # if not b'\0\0' it is already handled
            if lookupState != b'\0\0\0': # check to insure it isn't meant to return None
                print("It has already been handled")
                return lookupState.decode('utf-8') # so just return it back
            else:
                return None
        else: # it is b'\0\0' so just wait on the channel
            print("We are going to wait on a channel")
            while True:
                result = channelClient.get_message()
                
                if result and not result["data"] == 1:
                    result = result['data'].decode('utf-8')
                    print("We got a result on the channel:", result)
                    if result == '\0\0\0': # meant to return None
                        return None
                    return result
    else: # nothing is handling it so you have to handle it
        print("Nothing is handling it we are going to handle it")
        redisClient.set(cityName, '\0\0') # we are declaring we are handling it

        global s
        global csrfToken
        if csrfToken is None:
            response = s.get("https://www.booking.com/", headers=headers)
            soup=BeautifulSoup(response.content,'lxml').prettify()
            csrfToken = str(soup).split("'X-Booking-CSRF': '", 1)[1].split("'",1)[0]

        headers["X-Booking-Csrf"] = csrfToken
        headers["X-Booking-Client-Info"] = "wqhje213213jhk123h"

        url = "https://www.booking.com/autocomplete_csrf?v=1&lang=en-us&aid=eedwqe&pid=ku123dd213&term=" + cityName

        response2 = s.get(url, headers=headers)

        response_json = json.loads(response2.content)
    
        try:
            destID = response_json['city'][0]['dest_id']
        except:
            destID = None

        if destID[0] != "-": # if first character of the destID is not '-'
            destID = None

        if destID is None:
            redisClient.set(cityName, '\0\0\0')
            redisClient.publish(cityName, '\0\0\0')
        else:
            redisClient.set(cityName, destID)
            redisClient.publish(cityName, destID)

        redisClient.expire(cityName, 1) # expire after a second
        return destID 
        
