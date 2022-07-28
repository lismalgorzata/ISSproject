import json
import sys
import gmaps
from configparser import ConfigParser
from urllib import error, request
import geopy.distance
from geopy.geocoders import Nominatim
from sklearn.preprocessing import MinMaxScaler

BASE_GEOLOCATION_API_URL = "https://api.ipgeolocation.io/ipgeo"
BASE_ISS_API_URL = "https://api.wheretheiss.at/v1/satellites"
URL = 'http://api.open-notify.org/iss-now.json'

# USER INFO
def _get_location_api_key():
    config = ConfigParser()
    config.read("hidden.ini")
    return config["ipgeolocation"]["api_key_geoloc"]


def build_location_query():
    api_key = _get_location_api_key()
    url = f"{BASE_GEOLOCATION_API_URL}?apiKey={api_key}"
    return url


def get_user_location_data(user_query_url):
    try:
        response = request.urlopen(user_query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_user_location_info(user_location_data):
    country = user_location_data["country_name"]
    latitude = user_location_data["latitude"]
    longitude = user_location_data["longitude"]
    scaler_latitude = MinMaxScaler((-90, 90))
    scaler_longitude = MinMaxScaler((-180, 180))

    print("YOUR LOCATION")
    print(f"Country: {country}")
    print(f"Longitude: {longitude}")
    print(f"Latitude: {latitude}")


# ISS INFO
def build_iss_query():
    iss_id = 25544
    url = f"{BASE_ISS_API_URL}/{iss_id}"
    return url


def get_iss_location_data(iss_query_url):
    try:
        response = request.urlopen(iss_query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:  # 404 - Not Found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_iss_location_info(iss_location_data):
    latitude = str(iss_location_data["latitude"])
    longitude = str(iss_location_data["longitude"])
    scaler_latitude = MinMaxScaler((-90, 90))
    scaler_longitude = MinMaxScaler((-180, 180))
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse(latitude + "," + longitude)
    try:
        address = location.raw['address']
        country = address.get('country', '')

        print("ISS LOCATION")
        print(f"Country: {country}")
        print(f"Longitude: {longitude}")
        print(f"Latitude: {latitude}")

    except AttributeError:
        print("ISS LOCATION")
        print(f"Longitude: {longitude}")
        print(f"Latitude: {latitude}")
        print("Impossible to detect the country")

def _get_geocoding_api_key():
    config = ConfigParser()
    config.read("hidden.ini")
    return config["geocoding"]["api_key_geocod"]

def map_show(user_location_data, iss_location_data):
    api_key = _get_geocoding_api_key()
    gmaps.configure(api_key=api_key)

    user_latitude = user_location_data["latitude"]
    user_longitude = user_location_data["longitude"]
    user_coords = (user_longitude, user_latitude)

    iss_latitude = iss_location_data["latitude"]
    iss_longitude = iss_location_data["longitude"]
    iss_coords = (iss_longitude, iss_latitude)

    fig = gmaps.figure()  # create the layer
    layer = gmaps.directions.Directions(user_coords, iss_coords, mode='satellite')
    fig.add_layer(layer)
    return fig


def get_distance(user_location_data, iss_location_data):
    scaler_latitude = MinMaxScaler((-90, 90))
    scaler_longitude = MinMaxScaler((-180, 180))

    user_latitude = user_location_data["latitude"]
    user_longitude = user_location_data["longitude"]
    user_coords = (scaler_longitude.fit_transform(user_longitude), scaler_latitude.fit_transform(user_latitude))

    iss_latitude = iss_location_data["latitude"]
    iss_longitude = iss_location_data["longitude"]
    iss_coords = (scaler_longitude.fit_transform(iss_longitude), scaler_latitude.fit_transform(iss_latitude))

    distance = geopy.distance.geodesic(user_coords, iss_coords).km
    distance = str(round(distance, 2))

    print(f"You are {distance} km far from ISS!")
    print(f"")


# USER
user_query_url = build_location_query()
user_location_data = get_user_location_data(user_query_url)
display_user_location_info(user_location_data)
# ISS
iss_query_url = build_iss_query()
iss_location_data = get_iss_location_data(iss_query_url)
display_iss_location_info(iss_location_data)
# INFO
get_distance(user_location_data, iss_location_data)
map_show(user_location_data, iss_location_data)