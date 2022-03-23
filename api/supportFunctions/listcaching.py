from api.models import CachedListHotels, Hotel, City, CachedListRestaurants
import hashlib
import json
from django.utils import timezone
from django.conf import settings

def cacheResultHotel(city_obj, hotels, keywords): #hotels is an ordered array ; keywords is a string
    keywords = sorted(keywords.split(" ")) # turn into an array; sort the array
    print(keywords)
    md5hash = hashlib.md5(json.dumps(keywords).encode('utf-8')).hexdigest() # this is the md5 hash of the keywords``
    try:
        cachedList = CachedListHotels.objects.update_or_create(city=city_obj, keywordHash=md5hash)[0]
        cachedList.hotels.add(*hotels)
        print("Cached the list")
        return True
    except Exception as e:
        print(e)
        return False

def getCachedResultHotel(city_obj, keywords):
    keywords = sorted(keywords.split(" ")) # turn into an array; sort the array
    md5hash = hashlib.md5(json.dumps(keywords).encode('utf-8')).hexdigest() # this is the md5 hash of the keywords
    pastdate = timezone.now() - settings.CACHED_LIST_LIFETIME
    print(pastdate)
    try:
        cachedList = CachedListHotels.objects.get(city=city_obj, keywordHash=md5hash, cached_on__range=(pastdate, timezone.now()))
    except Exception as e:
        print(e)
        return None # if there is no such result -> return None
    
    return cachedList.hotels.all()


def cacheResultRestaurant(city_obj, restaurants, keywords): #hotels is an ordered array ; keywords is a string
    keywords = sorted(keywords.split(" ")) # turn into an array; sort the array
    print(keywords)
    md5hash = hashlib.md5(json.dumps(keywords).encode('utf-8')).hexdigest() # this is the md5 hash of the keywords``
    try:
        cachedList = CachedListRestaurants.objects.update_or_create(city=city_obj, keywordHash=md5hash)[0]
        cachedList.restaurants.add(*restaurants)
        print("Cached the list")
        return True
    except Exception as e:
        print(e)
        return False

def getCachedResultRestaurant(city_obj, keywords):
    keywords = sorted(keywords.split(" ")) # turn into an array; sort the array
    md5hash = hashlib.md5(json.dumps(keywords).encode('utf-8')).hexdigest() # this is the md5 hash of the keywords
    pastdate = timezone.now() - settings.CACHED_LIST_LIFETIME
    print(pastdate)
    try:
        cachedList = CachedListRestaurants.objects.get(city=city_obj, keywordHash=md5hash, cached_on__range=(pastdate, timezone.now()))
    except Exception as e:
        print(e)
        return None # if there is no such result -> return None
    
    return cachedList.restaurants.all()