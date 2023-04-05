from libs import *

# GETTING latitude and longitude for map

# function to find the coordinate
# of a given city 
def findGeocode(city):
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout  
    try:
        # Specify the user_agent as your
        # app name it should not be none
        geolocator = Nominatim(user_agent="your_app_name")
        return geolocator.geocode(city)
    except GeocoderTimedOut:
        return findGeocode(city)  


def get_geolocation(df):    
    # each value from city column
    # will be fetched and sent to
    # function find_geocode   
    for i in (df["location"]):
        if findGeocode(i) != None:
            loc = findGeocode(i)
            # coordinates returned from function 
            df["latitude"] = loc.latitude
            print("lat", loc.latitude)
            df["longitude"] = loc.longitude
        else:
            df["latitude"] = loc.latitude
            df["longitude"] = loc.longitude
       
    return df